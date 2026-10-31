! Independent API consumer; MIT: licenses/regrid-rk45-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use regridpack_module,only:regrid
   implicit none
   integer,parameter::sizes(*)=[4,7,12]
   real(wp),parameter::scales(*)=[-2.0_wp,0.5_wp,3.0_wp]
   real(wp),allocatable::x(:),y(:),xx(:),q(:),expected(:),sx(:),sy(:),st(:)
   real(wp)::t,f,value,worst,normalization
   integer::n,m,is,grid,method,degree,i,j,c,idx,status,calls,points,rejected
   real(wp)::bad(4),out(2)
   calls=0; points=0; rejected=0; worst=0
   do is=1,size(sizes)
      n=sizes(is); m=4*n-2
      allocate(x(n),y(n),xx(m),q(m),expected(m),sx(n),sy(n),st(m))
      do grid=1,2
         do i=1,n
            t=real(i-1,wp)/real(n-1,wp)
            if (grid==2) t=t*t
            x(i)=-2+5*t
         end do
         idx=0
         do i=1,n-1
            do j=0,3
               idx=idx+1
               xx(idx)=x(i)+real(j,wp)*(x(i+1)-x(i))/4
            end do
         end do
         xx(m-1:m)=x(n)
         do c=1,size(scales)
            do method=1,3,2
               do degree=0,method
                  y=scales(c)*x**degree
                  expected=scales(c)*xx**degree
                  call checked_call(method)
               end do
            end do
            ! Linear interpolation of nonaffine data: independently locate intervals.
            y=scales(c)*x*x
            do j=1,m
               i=1
               do while(i<n-1)
                  if (xx(j)<=x(i+1)) exit
                  i=i+1
               end do
               f=(xx(j)-x(i))/(x(i+1)-x(i))
               expected(j)=(1-f)*y(i)+f*y(i+1)
            end do
            call checked_call(1)
         end do
      end do
      deallocate(x,y,xx,q,expected,sx,sy,st)
   end do
   ! Wrapper diagnostics: outputs on failed calls are intentionally not inspected.
   call regrid([0.0_wp,1.0_wp],[1.0_wp],[0.5_wp],out(:1),1,status)
   call expect_status(10)
   call regrid([0.0_wp,1.0_wp],[1.0_wp,2.0_wp],[0.5_wp],out(:1),2,status)
   call expect_status(6)
   call regrid([0.0_wp],[1.0_wp],[0.0_wp],out(:1),1,status)
   call expect_status(2)
   call regrid([0.0_wp,1.0_wp],[1.0_wp,2.0_wp],[0.5_wp],out(:1),3,status)
   call expect_status(2)
   call regrid([0.0_wp,1.0_wp],[1.0_wp,2.0_wp],[-0.1_wp],out(:1),1,status)
   call expect_status(3)
   call regrid([0.0_wp,1.0_wp],[1.0_wp,2.0_wp],[1.1_wp],out(:1),1,status)
   call expect_status(3)
   bad=[0.0_wp,1.0_wp,1.0_wp,3.0_wp]
   call regrid(bad,bad,[0.5_wp,2.5_wp],out,1,status)
   call expect_status(4)
   bad=[0.0_wp,1.0_wp,2.0_wp,3.0_wp]
   call regrid(bad,bad,[2.5_wp,0.5_wp],out,1,status)
   call expect_status(4)
   call regrid(bad,2*bad+1,[0.5_wp,2.5_wp],out,3,status)
   if (status/=0.or..not.all(ieee_is_finite(out))) error stop 'recovery status'
   if (maxval(abs(out-[2.0_wp,6.0_wp]))>1e-12_wp) error stop 'recovery answer'
   calls=calls+1; points=points+2
   if (calls/=127.or.points/=3614.or.rejected/=8) error stop 'accounting'
   print '(a,i0,a,i0)', 'Successful regrids: ',calls,'; analytical value checks: ',points
   print '(a,i0)', 'Expected rejected requests: ',rejected
   print '(a)', 'Uniform/nonuniform grids; linear/cubic monomials and piecewise-linear references.'
   print '(a,es12.4)', 'Maximum normalized interpolation error: ',worst
   print '(a)', 'PASS regridpack-polynomial-reference'
contains
   subroutine checked_call(interpolation)
      integer,intent(in)::interpolation
      sx=x; sy=y; st=xx
      call regrid(x,y,xx,q,interpolation,status)
      if (status/=0) error stop 'interpolation status'
      if (.not.all(ieee_is_finite(q))) error stop 'nonfinite values'
      if (any(x/=sx).or.any(y/=sy).or.any(xx/=st)) error stop 'changed input'
      normalization=max(1.0_wp,maxval(abs(expected)))
      value=maxval(abs(q-expected))/normalization
      if (value>2e-12_wp) error stop 'analytical interpolation reference'
      worst=max(worst,value)
      calls=calls+1; points=points+size(q)
   end subroutine
   subroutine expect_status(code)
      integer,intent(in)::code
      if (status/=code) error stop 'unexpected rejection code'
      rejected=rejected+1
   end subroutine
end program
