! Adapted author public-API examples; independent references and identities.
! MIT License
! 
! Copyright (c) 2022-2026 Federico Perini
! Copyright (c) 2021-2022 Michael Helton, Oscar Smith, and the Bessels.jl contributors
! 
! Permission is hereby granted, free of charge, to any person obtaining a copy
! of this software and associated documentation files (the "Software"), to deal
! in the Software without restriction, including without limitation the rights
! to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
! copies of the Software, and to permit persons to whom the Software is
! furnished to do so, subject to the following conditions:
! 
! The above copyright notice and this permission notice shall be included in all
! copies or substantial portions of the Software.
! 
! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
! IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
! FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
! AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
! LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
! OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
! SOFTWARE.
program checked_special_functions
   use ieee_arithmetic, only: ieee_is_finite
   use bessels, only: wp=>BK,besseli0,besseli1,besselk0,besselk1
   implicit none
   real(wp), parameter :: arguments(7)=[0.125_wp,0.25_wp,0.5_wp,1._wp,2._wp,4._wp,8._wp]
   ! mpmath 1.3.0, 80 decimal digits; rows are I0,I1,K0,K1 at each argument.
   real(wp), parameter :: references(4,7)=reshape([ &
      1.0039100663533544851278_wp,0.062622149811234825444244_wp,2.2078690867449700600076_wp,7.8311182991157511634643_wp, &
      1.0156861412236079233547_wp,0.12597910894546792590771_wp,1.5415067512483028161695_wp,3.7470259744407116380341_wp, &
      1.0634833707413235192632_wp,0.25789430539089631636248_wp,0.92441907122766586178192_wp,1.6564411200033008936964_wp, &
      1.2660658777520083355982_wp,0.5651591039924850272077_wp,0.42102443824070833333563_wp,0.60190723019723457473754_wp, &
      2.2795853023360672674372_wp,1.5906368546373290633823_wp,0.11389387274953343565272_wp,0.1398658818165224272846_wp, &
      11.301921952136330496356_wp,9.7594651537044499094752_wp,0.011159676085853024269745_wp,0.012483498887268431470384_wp, &
      427.5641157218047851774_wp,399.87313678256009821908_wp,0.00014647070522281538709658_wp,0.00015536921180500113391686_wp],[4,7])
   real(wp) :: x,values(4),series_values(2),relative_error,series_error,identity_error
   real(wp) :: max_reference_error,max_series_error,max_identity_error
   integer :: j
   max_reference_error=0._wp; max_series_error=0._wp; max_identity_error=0._wp
   print '(a,i0)', 'Bessel kind precision (decimal digits): ',precision(1._wp)
   print '(a)', '       x       relative table error     relative I-series error   Wronskian residual'
   do j=1,size(arguments)
      x=arguments(j)
      values=[besseli0(x),besseli1(x),besselk0(x),besselk1(x)]
      if (.not.all(ieee_is_finite(values)).or.any(values<=0._wp)) error stop 'invalid positive-argument Bessel values'
      relative_error=maxval(abs(values-references(:,j))/references(:,j))
      call independent_i_series(x,series_values)
      series_error=maxval(abs(values(1:2)-series_values)/series_values)
      identity_error=abs(x*(values(1)*values(4)+values(2)*values(3))-1._wp)
      if (max(relative_error,series_error)>2.e-12_wp.or.identity_error>1.e-11_wp) &
         error stop 'independent modified Bessel checks'
      max_reference_error=max(max_reference_error,relative_error)
      max_series_error=max(max_series_error,series_error)
      max_identity_error=max(max_identity_error,identity_error)
      print '(f8.3,3es24.8)',x,relative_error,series_error,identity_error
   end do
   print '(a,es12.4)', 'Maximum relative table error (all four functions): ',max_reference_error
   print '(a,es12.4)', 'Maximum relative I0/I1 series error: ',max_series_error
   print '(a,es12.4)', 'Maximum Wronskian residual: ',max_identity_error
   print '(a)', 'PASS bessels-modified-values'
contains
   subroutine independent_i_series(x,sums)
      real(wp), intent(in) :: x
      real(wp), intent(out) :: sums(2)
      real(wp) :: terms(2),factor
      integer :: k
      factor=x*x/4._wp; terms=[1._wp,x/2._wp]; sums=terms
      do k=1,1000
         terms(1)=terms(1)*factor/real(k*k,wp)
         terms(2)=terms(2)*factor/real(k*(k+1),wp)
         sums=sums+terms
         if (all(terms<=epsilon(1._wp)*sums)) return
      end do
      error stop 'independent I-series did not converge'
   end subroutine
end program
