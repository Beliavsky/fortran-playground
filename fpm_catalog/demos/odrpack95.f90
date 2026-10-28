module line_model
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
   end subroutine line
end module line_model

program main
   use line_model
   use odrpack, only: odr,odrpack_model
   implicit none
   type(odrpack_model) :: model
   real(dp) :: x(6,1),y(6,1),beta(2),xc(6),yc(6),sxx,syy,sxy,slope,intercept
   integer :: info,i
   x(:,1)=[(real(i,dp),i=0,5)]
   y(:,1)=[1.1_dp,2.9_dp,5.1_dp,6.9_dp,9.1_dp,10.9_dp]
   beta=[0._dp,1._dp]
   model%fcn=>line
   ! Orthogonal distance regression treats errors in both x and y.
   call odr(model,6,1,1,2,beta,y,x,job=20,iprint=0,info=info)
   xc=x(:,1)-sum(x(:,1))/6
   yc=y(:,1)-sum(y(:,1))/6
   sxx=sum(xc**2); syy=sum(yc**2); sxy=sum(xc*yc)
   slope=(syy-sxx+sqrt((syy-sxx)**2+4*sxy**2))/(2*sxy)
   intercept=sum(y(:,1))/6-slope*sum(x(:,1))/6
   if (info<1.or.info>3) error stop 'ODR convergence failed'
   if (maxval(abs(beta-[intercept,slope]))>1e-5_dp) error stop 'ODR differs from analytic TLS'
   print '(a,2f12.6)', 'Intercept and slope:',beta
   print '(a,f12.6)', 'Maximum vertical residual:',maxval(abs(y(:,1)-beta(1)-beta(2)*x(:,1)))
   print *, 'PASS odrpack95'
end program main
