! Adapted author public-API examples; independent references and identities.
! MIT License
! 
! Copyright (c) 2022 arjenmarkus
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
   use iso_fortran_env, only: wp=>real64
   use fullerton_gamma, only: fgamma,log_gamma,reciprocal_gamma
   implicit none
   real, parameter :: arguments(7)=[0.5,1.,1.5,2.,2.5,5.,10.]
   real(wp) :: reference(7),pi,values(3),errors(3),maximum_errors(3)
   integer :: j
   pi=acos(-1._wp)
   ! Factorials and half-integer Gamma identities, computed independently in real64.
   reference=[sqrt(pi),1._wp,sqrt(pi)/2._wp,1._wp,3._wp*sqrt(pi)/4._wp,24._wp,362880._wp]
   maximum_errors=0._wp
   print '(a,i0)', 'Default-real precision (decimal digits): ',precision(1.)
   print '(a)', '       x        Gamma(x)           relative Gamma error   scaled log error   relative reciprocal error'
   do j=1,size(arguments)
      values=[real(fgamma(arguments(j)),wp),real(log_gamma(arguments(j)),wp),real(reciprocal_gamma(arguments(j)),wp)]
      if (.not.all(ieee_is_finite(values))) error stop 'nonfinite Gamma-family result'
      errors(1)=abs(values(1)-reference(j))/reference(j)
      errors(2)=abs(values(2)-log(reference(j)))/max(1._wp,abs(log(reference(j))))
      errors(3)=abs(values(3)*reference(j)-1._wp)
      if (maxval(errors)>3.e-6_wp) error stop 'independent Gamma-family values'
      maximum_errors=max(maximum_errors,errors)
      print '(f8.2,es20.10,3es20.6)', arguments(j),values(1),errors
   end do
   print '(a,3es12.4)', 'Maximum Gamma/log/reciprocal errors: ',maximum_errors
   print '(a)', 'PASS fullerton-gamma-values'
end program
