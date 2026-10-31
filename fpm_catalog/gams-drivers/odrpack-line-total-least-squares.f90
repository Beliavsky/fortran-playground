! Author model-callback pattern adapted on 2026-10-30 to closed-form line fitting checks.
! MIT License
! 
! Copyright (c) 2024, Hugo Vale
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
module orthogonal_line_model
   use odrpack_kinds, only: dp
   use iso_c_binding, only: c_ptr
   implicit none
contains
   pure subroutine line(n,m,q,np,ldifx,beta,xplusd,ifixb,ifixx,ideval,f,fjacb,fjacd,istop,data)
      integer, intent(in) :: n,m,q,np,ldifx,ideval,ifixb(np),ifixx(ldifx,m)
      real(dp), intent(in) :: beta(np),xplusd(n,m)
      real(dp), intent(out) :: f(n,q),fjacb(n,np,q),fjacd(n,m,q)
      integer, intent(out) :: istop
      type(c_ptr), value, intent(in) :: data
      istop=0
      if (mod(ideval,10)>0) f(:,1)=beta(1)+beta(2)*xplusd(:,1)
      if (mod(ideval/10,10)>0) then
         fjacb(:,1,1)=1._dp
         fjacb(:,2,1)=xplusd(:,1)
      end if
      if (mod(ideval/100,10)>0) fjacd(:,1,1)=beta(2)
   end subroutine
end module
program checked_orthogonal_regression
   use orthogonal_line_model
   use odrpack, only: odr,odrpack_model
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=6
   type(odrpack_model) :: model
   real(dp) :: x(n,1),y(n,1),beta(2),xc(n),yc(n),sxx,syy,sxy,d,reference(2)
   real(dp) :: objective,exact_objective,parameter_error
   integer :: i,problem,status
   model%fcn=>line
   do problem=1,2
      if (problem==1) then
         x(:,1)=[(real(i,dp),i=0,n-1)]
         y(:,1)=1._dp+2._dp*x(:,1)+[0.1_dp,-0.1_dp,0.1_dp,-0.1_dp,0.1_dp,-0.1_dp]
         beta=[0._dp,1._dp]
      else
         x(:,1)=[(10._dp+real(i,dp),i=0,n-1)]
         y(:,1)=-3._dp-1.5_dp*x(:,1)+[0.2_dp,-0.1_dp,0.1_dp,-0.2_dp,0.05_dp,-0.05_dp]
         beta=[0._dp,-1._dp]
      end if
      xc=x(:,1)-sum(x(:,1))/n;yc=y(:,1)-sum(y(:,1))/n
      sxx=sum(xc**2);syy=sum(yc**2);sxy=sum(xc*yc)
      d=sqrt((syy-sxx)**2+4._dp*sxy**2)
      reference(2)=(syy-sxx+d)/(2._dp*sxy)
      reference(1)=sum(y(:,1))/n-reference(2)*sum(x(:,1))/n
      exact_objective=0.5_dp*(sxx+syy-d)
      ! JOB=20 supplies and checks analytic model derivatives. Default weights are one in x and y.
      call odr(model,n,1,1,2,beta,y,x,job=20,iprint=0,info=status)
      if (status<1.or.status>3) error stop 'orthogonal regression did not converge'
      if (.not.all(ieee_is_finite(beta))) error stop 'nonfinite regression coefficients'
      parameter_error=maxval(abs(beta-reference))
      objective=sum((y(:,1)-beta(1)-beta(2)*x(:,1))**2)/(1._dp+beta(2)**2)
      if (.not.ieee_is_finite(objective)) error stop 'nonfinite orthogonal objective'
      if (parameter_error>1.e-5_dp.or.abs(objective-exact_objective)>1.e-8_dp) &
         error stop 'closed-form total least squares mismatch'
      print '(a,i0,a,i0)', 'Line case ',problem,' status=',status
      print '(a,2f17.10)', 'Fitted intercept/slope:',beta
      print '(a,2f17.10)', 'Exact TLS coefficients:',reference
      print '(a,2es15.6)', 'Orthogonal sum of squares / exact:',objective,exact_objective
      print '(a,es12.4)', 'Maximum parameter error:',parameter_error
   end do
   print '(a)', 'PASS odrpack-line-total-least-squares'
end program
