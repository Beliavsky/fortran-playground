program demo_nafpack
   use NAFPack_kinds, only: sp
   use NAFPack_Fourier_Transform, only: Fourier_Transform,ALG_RADIX2_DIT,idft
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=16
   type(Fourier_Transform) :: transform
   complex(sp) :: signal(n),expected(n),spectrum(n)
   complex(sp), allocatable :: recovered(:)
   real(sp) :: theta,real_part(n),imaginary_part(n),spectrum_error,roundtrip_error
   integer :: i
   do i=1,n
      theta = 2*acos(-1.0_sp)*real(i-1,sp)/n
      signal(i) = cmplx(cos(3*theta),sin(3*theta),sp)+0.25_sp*cmplx(cos(5*theta),sin(5*theta),sp)
   end do
   expected = cmplx(0.0_sp,0.0_sp,sp)
   expected(4) = real(n,sp); expected(6) = real(n,sp)/4
   call transform%create_fft_plan_sp(n,algorithm=ALG_RADIX2_DIT)
   call transform%execute_fft_plan_sp(real(signal,sp),aimag(signal),real_part,imaginary_part)
   spectrum = cmplx(real_part,imaginary_part,sp)
   call transform%destroy_fft_plan_sp()
   recovered = idft(spectrum)
   if (.not. all(ieee_is_finite(real(spectrum)))) error stop 'Nonfinite spectrum'
   if (.not. all(ieee_is_finite(aimag(spectrum)))) error stop 'Nonfinite spectrum'
   if (.not. all(ieee_is_finite(real(recovered)))) error stop 'Nonfinite reconstruction'
   if (.not. all(ieee_is_finite(aimag(recovered)))) error stop 'Nonfinite reconstruction'
   spectrum_error = maxval(abs(spectrum-expected))
   roundtrip_error = maxval(abs(recovered-signal))
   if (spectrum_error>1e-4_sp) error stop 'Known frequency amplitudes differ'
   if (roundtrip_error>1e-5_sp) error stop 'Inverse transform differs'
   print '(a)', 'Sixteen complex samples: frequency 3 plus frequency 5 at quarter amplitude.'
   print '(a)', 'Frequency   Fourier amplitude'
   do i=1,n
      if (abs(spectrum(i))>1e-4_sp) print '(i6,f20.8)',i-1,abs(spectrum(i))
   end do
   print '(a,es12.3)', 'Maximum spectral error: ',spectrum_error
   print '(a,es12.3)', 'Maximum round-trip error: ',roundtrip_error
   print '(a)', 'PASS nafpack'
end program
