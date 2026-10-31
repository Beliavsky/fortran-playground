! Independent API consumer; MIT: licenses/circuits-beta-drivers-MIT.txt.
program elementary_reference
   use assert, only: wp
   use funcs, only: sinc,sech
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp) :: x(133),s(133),h(133),reference,term,a,max_sinc_error,max_sech_error
   integer :: i,k
   x(:129) = [(real(i,wp)/8,i=-64,64)]
   x(130:) = [-1.e-10_wp,1.e-10_wp,-1.e-6_wp,1.e-6_wp]
   s = sinc(x)
   h = sech(x)
   if (.not. all(ieee_is_finite(s)) .or. .not. all(ieee_is_finite(h))) error stop 'nonfinite function'
   max_sinc_error = 0._wp
   max_sech_error = 0._wp
   do i = 1,size(x)
      term = 1._wp
      reference = term
      ! Independent sinc series: sum (-x*x)**k/(2*k+1)!, no sin call.
      do k = 1,63
         term = -term*x(i)*x(i)/real((2*k)*(2*k+1),wp)
         reference = reference+term
      end do
      max_sinc_error = max(max_sinc_error,abs(s(i)-reference))
      a = exp(-abs(x(i)))
      reference = 2*a/(1+a*a)
      max_sech_error = max(max_sech_error,abs(h(i)-reference))
      if (abs(sinc(x(i))-s(i)) > 1.e-14_wp) error stop 'scalar/array sinc'
      if (abs(sech(x(i))-h(i)) > 1.e-14_wp) error stop 'scalar/array sech'
      if (h(i) <= 0 .or. h(i) > 1) error stop 'sech range'
   end do
   if (max_sinc_error > 5.e-13_wp) error stop 'sinc power series reference'
   if (max_sech_error > 5.e-14_wp) error stop 'sech exponential reference'
   if (s(65) /= 1 .or. h(65) /= 1) error stop 'values at zero'
   if (maxval(abs(s(:129)-s(129:1:-1))) > 1.e-14_wp) error stop 'sinc even symmetry'
   if (maxval(abs(h(:129)-h(129:1:-1))) > 1.e-14_wp) error stop 'sech even symmetry'
   print '(a)', '133 real arguments: -8..8 step 0.125, plus signed near-zero values.'
   print '(a,es12.4)', 'Maximum sinc absolute error versus 64-term power series: ',max_sinc_error
   print '(a,es12.4)', 'Maximum sech absolute error versus exponential formula: ',max_sech_error
   print '(a)', 'Zero values, even symmetry, sech range and scalar/array consistency checked.'
   print '(a)', 'PASS rpn-sinc-sech-reference'
end program elementary_reference
