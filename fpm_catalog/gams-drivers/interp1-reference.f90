! Independent API consumer; MIT: licenses/least-interpolation-drivers-MIT.txt.
program main
   use iso_fortran_env,only:real64
   use ieee_arithmetic,only:ieee_is_finite,ieee_is_nan
   use interpolation,only:interp1
   implicit none
   character(6),parameter::methods(*)=[character(6)::'linear','pchip','cubic']
   real(real64),parameter::slope(3)=[2.0_real64,-0.75_real64,0.0_real64],offset(3)=[1.0_real64,2.0_real64,-3.0_real64]
   real(real64)::x(5),y(3,5),query(41),got(3,41),one(41),point(3),extra(3,2),outside(2)
   real(real64)::dense(129),smooth(129),knots(5),profile(5),hx(3),hy(3),t,reference,worst,lower,upper
   integer::grid,method,i,c,profile_id,sgn,interval,nref,nnan,nbound,nmono,affine_refs,hump_refs
   worst=0; nref=0; nnan=0; nbound=0; nmono=0
   query=[(-2.0_real64+real(i,real64)/10,i=0,40)]; outside=[-3.0_real64,3.0_real64]
   do grid=1,2
      x=[-2.0_real64,-1.0_real64,0.0_real64,1.0_real64,2.0_real64]
      if (grid==2) x=[-2.0_real64,-1.5_real64,-0.25_real64,0.5_real64,2.0_real64]
      do c=1,3
         y(c,:)=slope(c)*x+offset(c)
      end do
      do method=1,size(methods)
         got=interp1(x,y,query,method=trim(methods(method)))
         do c=1,3
            one=interp1(x,y(c,:),query,method=trim(methods(method)))
            do i=1,size(query)
               reference=slope(c)*query(i)+offset(c)
               call check(got(c,i),reference); call check(one(i),reference)
               call check(interp1(x,y(c,:),query(i),method=trim(methods(method))),reference)
            end do
         end do
         do i=1,size(query)
            point=interp1(x,y,query(i),method=trim(methods(method)))
            do c=1,3
               call check(point(c),slope(c)*query(i)+offset(c))
            end do
         end do
         extra=interp1(x,y,outside,method=trim(methods(method)))
         if (.not.all(ieee_is_nan(extra))) error stop 'default out-of-range NaN'
         nnan=nnan+size(extra)
         extra=interp1(x,y,outside,method=trim(methods(method)),extrap='extrap')
         do c=1,3
            do i=1,2
               call check(extra(c,i),slope(c)*outside(i)+offset(c))
            end do
         end do
      end do
   end do
   affine_refs=nref
   do grid=1,2
      x=[-2.0_real64,-1.0_real64,0.0_real64,1.0_real64,2.0_real64]
      if (grid==2) x=[-2.0_real64,-1.5_real64,-0.25_real64,0.5_real64,2.0_real64]
      dense=[(-2.0_real64+real(i,real64)/32,i=0,128)]
      do profile_id=1,2
         profile=[0.0_real64,1.0_real64,1.0_real64,2.0_real64,3.0_real64]
         if (profile_id==2) profile=[0.0_real64,2.0_real64,-1.0_real64,3.0_real64,1.0_real64]
         do sgn=-1,1,2
            smooth=interp1(x,sgn*profile,dense,method='pchip')
            knots=interp1(x,sgn*profile,x,method='pchip')
            do i=1,size(x)
               call check(knots(i),sgn*profile(i))
            end do
            do i=1,size(dense)
               interval=1
               do while(interval<4)
                  if (dense(i)<=x(interval+1)) exit
                  interval=interval+1
               end do
               lower=min(sgn*profile(interval),sgn*profile(interval+1))
               upper=max(sgn*profile(interval),sgn*profile(interval+1))
               if (.not.ieee_is_finite(smooth(i))) error stop 'nonfinite shape interpolation'
               if (smooth(i)<lower-2e-12_real64.or.smooth(i)>upper+2e-12_real64) error stop 'interval overshoot'
               nbound=nbound+1
               if (profile_id==1.and.i>1) then
                  if (sgn*(smooth(i)-smooth(i-1)) < -2e-12_real64) error stop 'monotonicity'
                  nmono=nmono+1
               end if
            end do
         end do
      end do
   end do
   hump_refs=0
   hx=[0.0_real64,1.0_real64,2.0_real64]; hy=[0.0_real64,1.0_real64,0.0_real64]
   dense=[(real(i,real64)/64,i=0,128)]
   do method=2,3
      smooth=interp1(hx,hy,dense,method=trim(methods(method)))
      do i=1,size(dense)
         t=dense(i)
         if (t>1) t=2-t
         ! Endpoint secant slope 1 and stationary middle knot give this cubic.
         reference=-t**3+t**2+t
         call check(smooth(i),reference)
         hump_refs=hump_refs+1
      end do
   end do
   if (nref/=3286.or.nnan/=36.or.nbound/=1032.or.nmono/=512) error stop 'fixture accounting'
   print '(a,i0)', 'Exact affine references across all four overloads, including extrapolation: ',affine_refs
   print '(a,i0)', 'Exact mirrored cubic references (pchip/cubic aliases): ',hump_refs
   print '(a,4i6)', 'Total exact / NaN / interval-bound / monotonicity checks: ',nref,nnan,nbound,nmono
   print '(a,es12.4)', 'Maximum normalized exact-reference error: ',worst
   print '(a)', 'PASS interp1-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in)::actual,expected
      real(real64)::error
      if (.not.ieee_is_finite(actual)) error stop 'nonfinite interpolated value'
      error=abs(actual-expected)/max(1.0_real64,abs(expected))
      if (error>2e-12_real64) error stop 'exact interpolation reference'
      worst=max(worst,error); nref=nref+1
   end subroutine check
end program main
