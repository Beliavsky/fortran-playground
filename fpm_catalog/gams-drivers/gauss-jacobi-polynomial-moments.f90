! Adapted author API patterns; analytic integral and moment checks.
! The MIT License (MIT)
! 
! Copyright (c) 2023--present featom developers
! 
! Permission is hereby granted, free of charge, to any person obtaining
! a copy of this software and associated documentation files (the
! "Software"), to deal in the Software without restriction, including
! without limitation the rights to use, copy, modify, merge, publish,
! distribute, sublicense, and/or sell copies of the Software, and to
! permit persons to whom the Software is furnished to do so, subject to
! the following conditions:
! 
! The above copyright notice and this permission notice shall be
! included in all copies or substantial portions of the Software.
! 
! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
! EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
! MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
! IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
! CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
! TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
! SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
program checked_quadrature_rule
   use GaussJacobiQuad, only: gauss_jacobi
   use gjp_types, only: wp=>dp
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=4
   real(wp) :: x(n),w(n),alpha,beta,answer,exact,error,max_error
   character(:), allocatable :: method
   integer :: algorithm,weight_case,k
   do algorithm=1,2
      if (algorithm==1) then
         method='recurrence'
      else
         method='gw'
      end if
      do weight_case=1,2
         alpha=real(weight_case-1,wp);beta=0._wp
         call gauss_jacobi(n,alpha,beta,x,w,method)
         if (.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite(w))) error stop 'nonfinite nodes or weights'
         if (any(abs(x)>=1._wp).or.any(w<=0._wp)) error stop 'invalid nodes or weights'
         max_error=0._wp
         do k=0,2*n-1
            ! Integrate x**k for weight 1, or (1-x)*x**k for alpha=1, beta=0.
            exact=moment(k)
            if (weight_case==2) exact=exact-moment(k+1)
            answer=sum(w*x**k)
            error=abs(answer-exact)/max(1._wp,abs(exact))
            if (error>1.e-11_wp) error stop 'weighted polynomial moment mismatch'
            max_error=max(max_error,error)
         end do
         print '(a,a,f4.1,a,es12.4)',method,' alpha=',alpha,' maximum scaled moment error=',max_error
         print '(a,4f15.10)', 'Nodes:  ',x
         print '(a,4f15.10)', 'Weights:',w
      end do
   end do
   print '(a)', 'PASS gauss-jacobi-polynomial-moments'
contains
   pure real(wp) function moment(k) result(value)
      integer, intent(in) :: k
      value=0._wp
      if (mod(k,2)==0) value=2._wp/real(k+1,wp)
   end function
end program
