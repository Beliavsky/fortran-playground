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
   use fullerton_gamma, only: digamma
   implicit none
   real, parameter :: arguments(7)=[0.5,1.,1.5,2.,2.5,5.,10.]
   real, parameter :: recurrence_points(5)=[0.25,0.5,1.5,3.25,10.]
   real, parameter :: reflection_points(3)=[0.125,0.25,0.375]
   real(wp), parameter :: euler=0.577215664901532860606512090082402431_wp
   real(wp) :: reference(7),half_psi,value,pi,error,max_error,recurrence_error,reflection_error,z
   real :: x
   integer :: j
   pi=acos(-1._wp); half_psi=-euler-2._wp*log(2._wp)
   reference=[half_psi,-euler,half_psi+2._wp,1._wp-euler,half_psi+8._wp/3._wp, &
      25._wp/12._wp-euler,-euler]
   do j=1,9
      reference(7)=reference(7)+1._wp/real(j,wp)
   end do
   max_error=0._wp; recurrence_error=0._wp; reflection_error=0._wp
   print '(a,i0)', 'Default-real precision (decimal digits): ',precision(1.)
   print '(a)', '       x           psi(x)              absolute reference error'
   do j=1,size(arguments)
      value=real(digamma(arguments(j)),wp)
      if (.not.ieee_is_finite(value)) error stop 'nonfinite digamma value'
      error=abs(value-reference(j)); max_error=max(max_error,error)
      if (error>5.e-6_wp) error stop 'independent digamma reference'
      print '(f8.2,es24.12,es24.6)',arguments(j),value,error
   end do
   do j=1,size(recurrence_points)
      x=recurrence_points(j)
      value=real(digamma(x+1.),wp)-real(digamma(x),wp)-1._wp/real(x,wp)
      if (.not.ieee_is_finite(value)) error stop 'nonfinite digamma recurrence'
      recurrence_error=max(recurrence_error,abs(value))
   end do
   do j=1,size(reflection_points)
      x=reflection_points(j); z=real(x,wp)
      value=real(digamma(1.-x),wp)-real(digamma(x),wp)-pi/tan(pi*z)
      if (.not.ieee_is_finite(value)) error stop 'nonfinite digamma reflection'
      reflection_error=max(reflection_error,abs(value))
   end do
   if (max(recurrence_error,reflection_error)>5.e-6_wp) error stop 'digamma identities'
   print '(a,es12.4)', 'Maximum absolute reference error: ',max_error
   print '(a,es12.4)', 'Maximum recurrence residual: ',recurrence_error
   print '(a,es12.4)', 'Maximum reflection residual: ',reflection_error
   print '(a)', 'PASS fullerton-digamma-values'
end program
