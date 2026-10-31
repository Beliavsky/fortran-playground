! Independent API consumer; see licenses/multidimensional-fft-drivers-MIT.txt.
module independent_fourier_reference
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64), parameter :: pi=acos(-1.0_real64)
contains
   subroutine make_data(nx,ny,nz,fixture,data)
      integer, intent(in) :: nx,ny,nz,fixture
      complex(real64), intent(out) :: data(nx,ny,nz)
      integer :: i,j,k
      real(real64) :: angle
      data=0
      do k=0,nz-1
         do j=0,ny-1
            do i=0,nx-1
               select case(fixture)
               case(1)
               case(2)
                  data(i+1,j+1,k+1)=cmplx(1.25_real64,-0.75_real64,real64)
               case(3)
                  if (i==0.and.j==0.and.k==0) data(i+1,j+1,k+1)=1
               case(4)
                  if (i==nx-2.and.j==1.and.k==nz-1) &
                     data(i+1,j+1,k+1)=cmplx(0.5_real64,-0.25_real64,real64)
               case(5:6)
                  angle=2*pi*(real(i,real64)/nx+2*real(j,real64)/ny+real(k,real64)/nz)
                  if (fixture==6) angle=2*pi*(2*real(i,real64)/nx-real(j,real64)/ny-real(k,real64)/nz)
                  data(i+1,j+1,k+1)=cmplx(cos(angle),sin(angle),real64)
               case(7)
                  data(i+1,j+1,k+1)=cmplx(real(modulo(3*i+5*j+7*k,11)-5,real64)/4, &
                     real(modulo(7*i+2*j+3*k,13)-6,real64)/8,real64)
               case(8)
                  data(i+1,j+1,k+1)=cmplx(sin(0.7_real64*(i+2*j+3*k))+0.2_real64, &
                     cos(0.3_real64*(3*i-j+2*k))-0.4_real64,real64)
               end select
            end do
         end do
      end do
   end subroutine make_data
   subroutine direct_transform(data,reference)
      complex(real64), intent(in) :: data(:,:,:)
      complex(real64), intent(out) :: reference(:,:,:)
      integer :: i,j,k,a,b,c,nx,ny,nz
      real(real64) :: angle
      nx=size(data,1); ny=size(data,2); nz=size(data,3)
      reference=0
      do c=0,nz-1
         do b=0,ny-1
            do a=0,nx-1
               do k=0,nz-1
                  do j=0,ny-1
                     do i=0,nx-1
                        angle=-2*pi*(real(a*i,real64)/nx+real(b*j,real64)/ny+real(c*k,real64)/nz)
                        reference(a+1,b+1,c+1)=reference(a+1,b+1,c+1) &
                           +data(i+1,j+1,k+1)*cmplx(cos(angle),sin(angle),real64)
                     end do
                  end do
               end do
            end do
         end do
      end do
   end subroutine direct_transform
   subroutine compare(actual,reference,scale,worst)
      complex(real64), intent(in) :: actual(:),reference(:)
      real(real64), intent(in) :: scale
      real(real64), intent(inout) :: worst
      real(real64) :: error
      if (.not.all(ieee_is_finite(real(actual))).or..not.all(ieee_is_finite(aimag(actual)))) &
         error stop 'nonfinite Fourier result'
      error=maxval(abs(actual-reference))/(1+scale); worst=max(worst,error)
      if (error>2e-12_real64) error stop 'independent Fourier reference mismatch'
   end subroutine compare
end module independent_fourier_reference

program checked_decomp_fft
   use independent_fourier_reference
   use mpi
   use decomp_2d, only: decomp_2d_init,decomp_2d_finalize,decomp_log,decomp_info,alloc_x,alloc_z
   use decomp_2d_fft
   use decomp_2d_constants, only: D2D_LOG_QUIET,DECOMP_2D_FFT_FORWARD,DECOMP_2D_FFT_BACKWARD,PHYSICAL_IN_X
   implicit none
   integer, parameter :: dims(3,3)=reshape([4,3,2,5,4,3,6,5,4],[3,3])
   type(decomp_info), pointer :: physical
   complex(real64), allocatable :: input(:,:,:),output(:,:,:),original(:,:,:),reference(:,:,:),forward(:,:,:)
   integer :: code,processes,shape_id,nx,ny,nz,count,fixture,p_row,p_col,fixtures=0,entries=0
   real(real64) :: worst_forward=0,worst_inverse=0,worst_roundtrip=0,worst_energy=0,energy_error
   call MPI_Init(code); call check()
   call MPI_Comm_size(MPI_COMM_WORLD,processes,code); call check()
   if (processes/=1) error stop 'one MPI process required'
   do shape_id=1,3
      nx=dims(1,shape_id); ny=dims(2,shape_id); nz=dims(3,shape_id); count=nx*ny*nz
      decomp_log=D2D_LOG_QUIET; p_row=1; p_col=1
      call decomp_2d_init(nx,ny,nz,p_row,p_col,complex_pool=.true.)
      call decomp_2d_fft_init(PHYSICAL_IN_X)
      physical=>decomp_2d_fft_get_ph()
      call alloc_x(input,physical,.true.); call alloc_z(output,physical,.true.)
      if (any(shape(input)/=[nx,ny,nz]).or.any(shape(output)/=[nx,ny,nz])) &
         error stop 'unexpected single-process FFT layout'
      allocate(original(nx,ny,nz),reference(nx,ny,nz),forward(nx,ny,nz))
      do fixture=1,8
         call make_data(nx,ny,nz,fixture,original)
         call direct_transform(original,reference)
         input=original
         call decomp_2d_fft_3d(input,output,DECOMP_2D_FFT_FORWARD)
         forward=output
         call compare(reshape(forward,[count]),reshape(reference,[count]),sum(abs(original)),worst_forward)
         energy_error=abs(sum(abs(forward)**2)-count*sum(abs(original)**2))/(1+count*sum(abs(original)**2))
         worst_energy=max(worst_energy,energy_error)
         if (energy_error>2e-12_real64) error stop 'Parseval energy mismatch'
         ! Feed independently calculated Fourier coefficients to test the inverse separately.
         output=reference/real(count,real64)
         call decomp_2d_fft_3d(output,input,DECOMP_2D_FFT_BACKWARD)
         call compare(reshape(input,[count]),reshape(original,[count]),maxval(abs(original)),worst_inverse)
         output=forward/real(count,real64)
         call decomp_2d_fft_3d(output,input,DECOMP_2D_FFT_BACKWARD)
         call compare(reshape(input,[count]),reshape(original,[count]),maxval(abs(original)),worst_roundtrip)
         fixtures=fixtures+1; entries=entries+3*count
      end do
      deallocate(input,output,original,reference,forward)
      nullify(physical)
      call decomp_2d_fft_finalize()
      call decomp_2d_finalize()
   end do
   call MPI_Finalize(code); call check()
   print '(a,i0)', 'Complex data fixtures: ',fixtures
   print '(a,i0)', 'Forward/inverse/roundtrip entries: ',entries
   print '(a,es12.4)', 'Maximum normalized forward error: ',worst_forward
   print '(a,es12.4)', 'Maximum normalized independent inverse error: ',worst_inverse
   print '(a,es12.4)', 'Maximum normalized roundtrip error: ',worst_roundtrip
   print '(a,es12.4)', 'Maximum normalized Parseval error: ',worst_energy
   print '(a)', 'PASS decomp-3d-reference'
contains
   subroutine check()
      if (code/=MPI_SUCCESS) error stop 'MPI operation failed'
   end subroutine check
end program checked_decomp_fft
