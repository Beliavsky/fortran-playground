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

program checked_dtfft
   use independent_fourier_reference
   use iso_fortran_env, only: int32,int64
   use mpi_f08
   use dtfft
   implicit none
   integer(int32), parameter :: dims(2,3)=reshape([4,6,5,7,8,8],[2,3])
   complex(real64), pointer :: input(:,:),output(:,:)
   complex(real64), allocatable :: original(:,:,:),reference(:,:,:),forward(:,:,:)
   integer(int32) :: in_counts(2),out_counts(2),in_starts(2),out_starts(2),code,processes
   integer(int64) :: allocation_size
   integer :: shape_id,nx,ny,nz,count,fixture,fixtures=0,entries=0
   real(real64) :: worst_forward=0,worst_inverse=0,worst_roundtrip=0,worst_energy=0,energy_error
   call MPI_Init(code); call check()
   call MPI_Comm_size(MPI_COMM_WORLD,processes,code); call check()
   if (processes/=1) error stop 'one MPI process required'
   do shape_id=1,3
      block
      type(dtfft_plan_c2c_t) :: plan
      nx=dims(1,shape_id); ny=dims(2,shape_id); nz=1; count=nx*ny
      allocate(original(nx,ny,1),reference(nx,ny,1),forward(nx,ny,1))
      call plan%create(dims(:,shape_id),effort=DTFFT_ESTIMATE,executor=DTFFT_EXECUTOR_FFTW3,error_code=code)
      call check()
      call plan%get_local_sizes(in_counts=in_counts,out_counts=out_counts,in_starts=in_starts, &
         out_starts=out_starts,alloc_size=allocation_size,error_code=code)
      call check()
      ! Fourier output is a Y-aligned pencil: its Fortran storage axes are reversed.
      if (any(in_counts/=[nx,ny]).or.any(out_counts/=[ny,nx])) error stop 'unexpected FFT layout'
      if (any(in_starts/=0).or.any(out_starts/=0)) error stop 'unexpected local starts'
      call plan%mem_alloc(allocation_size,input,in_counts,error_code=code); call check()
      call plan%mem_alloc(allocation_size,output,out_counts,error_code=code); call check()
      do fixture=1,8
         call make_data(nx,ny,nz,fixture,original)
         call direct_transform(original,reference)
         input=original(:,:,1)
         call plan%execute(input,output,DTFFT_EXECUTE_FORWARD,error_code=code); call check()
         forward(:,:,1)=transpose(output)
         call compare(reshape(forward,[count]),reshape(reference,[count]),sum(abs(original)),worst_forward)
         energy_error=abs(sum(abs(forward)**2)-count*sum(abs(original)**2))/(1+count*sum(abs(original)**2))
         worst_energy=max(worst_energy,energy_error)
         if (energy_error>2e-12_real64) error stop 'Parseval energy mismatch'
         ! Feed independently calculated Fourier coefficients to test the inverse separately.
         output=transpose(reference(:,:,1))/real(count,real64)
         call plan%execute(output,input,DTFFT_EXECUTE_BACKWARD,error_code=code); call check()
         call compare(reshape(input,[count]),reshape(original,[count]),maxval(abs(original)),worst_inverse)
         output=transpose(forward(:,:,1))/real(count,real64)
         call plan%execute(output,input,DTFFT_EXECUTE_BACKWARD,error_code=code); call check()
         call compare(reshape(input,[count]),reshape(original,[count]),maxval(abs(original)),worst_roundtrip)
         fixtures=fixtures+1; entries=entries+3*count
      end do
      call plan%mem_free(input,code); call check()
      call plan%mem_free(output,code); call check()
      call plan%destroy(error_code=code); call check()
      deallocate(original,reference,forward)
      end block
   end do
   call MPI_Finalize(code); call check()
   print '(a,i0)', 'Complex data fixtures: ',fixtures
   print '(a,i0)', 'Forward/inverse/roundtrip entries: ',entries
   print '(a,es12.4)', 'Maximum normalized forward error: ',worst_forward
   print '(a,es12.4)', 'Maximum normalized independent inverse error: ',worst_inverse
   print '(a,es12.4)', 'Maximum normalized roundtrip error: ',worst_roundtrip
   print '(a,es12.4)', 'Maximum normalized Parseval error: ',worst_energy
   print '(a)', 'PASS dtfft-2d-reference'
contains
   subroutine check()
      if (code/=0) then
         print '(a,i0)', 'MPI/dtFFT status: ',code
         error stop 'MPI or dtFFT operation failed'
      end if
   end subroutine check
end program checked_dtfft
