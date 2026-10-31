! Independent API consumer; see licenses/dae-fft-drivers-MIT.txt.
program checked_nafpack_fft
   use iso_fortran_env, only: real64
   use NAFPack_kinds, only: sp
   use NAFPack_Fourier_Transform, only: Fourier_Transform,ALG_RADIX2_DIT,ALG_RADIX2_DIF
   use NAFPack_implementation_type, only: ITERATIVE,recursive
   use NAFPack_loop_method, only: init_loop_method
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: lengths(7)=[2,4,8,16,32,64,128]
   integer :: s,algorithm,pattern,scale,plans=0,transforms=0,coefficients=0
   real(real64) :: worst=0,worst_energy=0
   type(Fourier_Transform) :: transform
   do s=1,size(lengths)
      do algorithm=1,2
         do pattern=1,4
            do scale=1,3
               call fixture(lengths(s),algorithm,pattern,scale)
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Plan fixtures: ',plans
   print '(a,i0)', 'FFT calls including repetitions: ',transforms
   print '(a,i0)', 'Direct coefficient references: ',coefficients
   print '(a,es12.4)', 'Maximum L1-scaled coefficient error: ',worst
   print '(a,es12.4)', 'Maximum relative Parseval error: ',worst_energy
   print '(a)', 'PASS nafpack-fft-reference'
contains
   subroutine fixture(n,algorithm,pattern,scale)
      integer, intent(in) :: n,algorithm,pattern,scale
      real(sp) :: re(n),im(n),saved_re(n),saved_im(n),out_re(n),out_im(n),first_re(n),first_im(n)
      complex(real64) :: reference(n),value,phase
      real(real64) :: theta,pi,amplitude,normalization,error,energy,expected_energy
      integer :: j,k,implementation,repetition
      pi=acos(-1.0_real64); amplitude=16.0_real64**(scale-2)
      re=0; im=0
      do j=1,n
         theta=2*pi*real(j-1,real64)/n
         select case(pattern)
         case(1)
            if (j==max(1,n/2)) then
               re(j)=real(amplitude,sp); im(j)=real(-amplitude/2,sp)
            end if
         case(2)
            re(j)=real(amplitude,sp); im(j)=real(amplitude/4,sp)
         case(3)
            re(j)=real(amplitude*(cos(3*theta)+0.25_real64*cos(5*theta)),sp)
            im(j)=real(amplitude*(sin(3*theta)+0.25_real64*sin(5*theta)),sp)
         case(4)
            re(j)=real(amplitude*real(mod(7*j,19)-9,real64)/8,sp)
            im(j)=real(amplitude*real(mod(11*j,23)-11,real64)/16,sp)
         end select
      end do
      saved_re=re; saved_im=im
      normalization=sum(abs(cmplx(real(re,real64),real(im,real64),real64)))
      expected_energy=sum(real(re,real64)**2+real(im,real64)**2)
      do k=0,n-1
         value=cmplx(0.0_real64,0.0_real64,real64)
         do j=0,n-1
            theta=-2*pi*real(k*j,real64)/n
            phase=cmplx(cos(theta),sin(theta),real64)
            value=value+cmplx(real(re(j+1),real64),real(im(j+1),real64),real64)*phase
         end do
         reference(k+1)=value
      end do
      if (algorithm==1) then
         call transform%create_fft_plan_sp(n,algorithm=ALG_RADIX2_DIT)
      else
         call transform%create_fft_plan_sp(n,algorithm=ALG_RADIX2_DIF)
      end if
      do implementation=1,2
         do repetition=1,2
            out_re=-huge(1.0_sp); out_im=-huge(1.0_sp)
            if (implementation==1) then
               call transform%execute_fft_plan_sp(re,im,out_re,out_im, &
                  loop_method=init_loop_method(use_do_classic=.true.),implementation_type=ITERATIVE)
            else
               call transform%execute_fft_plan_sp(re,im,out_re,out_im, &
                  loop_method=init_loop_method(use_do_classic=.true.),implementation_type=recursive)
            end if
            if (any(re/=saved_re).or.any(im/=saved_im)) error stop 'input changed'
            if (.not.all(ieee_is_finite(out_re)).or..not.all(ieee_is_finite(out_im))) error stop 'nonfinite FFT'
            error=maxval(abs(cmplx(real(out_re,real64),real(out_im,real64),real64)-reference))/normalization
            energy=sum(real(out_re,real64)**2+real(out_im,real64)**2)/n
            worst=max(worst,error); worst_energy=max(worst_energy,abs(energy-expected_energy)/expected_energy)
            if (error>64*real(epsilon(1.0_sp),real64)) error stop 'direct DFT mismatch'
            if (abs(energy-expected_energy)/expected_energy>128*real(epsilon(1.0_sp),real64)) &
               error stop 'Parseval mismatch'
            if (repetition==1) then
               first_re=out_re; first_im=out_im
            else
               if (any(out_re/=first_re).or.any(out_im/=first_im)) error stop 'repeated FFT changed'
            end if
            transforms=transforms+1; coefficients=coefficients+n
         end do
      end do
      call transform%destroy_fft_plan_sp()
      plans=plans+1
   end subroutine fixture
end program checked_nafpack_fft
