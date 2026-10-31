! Independent API consumer; MIT: licenses/fitpack-polynomials-drivers-MIT.txt.
program main
   use fitpack,only:fitpack_curve,FP_REAL,FP_FLAG,FITPACK_SUCCESS
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   integer,parameter::sizes(*)=[8,13],orders(*)=[1,3,5]
   real(FP_REAL),parameter::scales(*)=[-2.0_FP_REAL,0.5_FP_REAL,3.0_FP_REAL]
   type(fitpack_curve)::curve
   real(FP_REAL),allocatable::x(:),y(:),saved_x(:),saved_y(:),values(:),nodes(:)
   real(FP_REAL)::targets(33),reference(33),scalar,t,worst,error,normalization
   integer(FP_FLAG)::status
   integer::is,n,grid,ik,k,degree,c,i,r,j,fits,checks
   fits=0; checks=0; worst=0
   targets=[(-0.5_FP_REAL+real(i-1,FP_REAL)/16,i=1,33)]
   do is=1,size(sizes)
      n=sizes(is)
      allocate(x(n),y(n),saved_x(n),saved_y(n))
      do grid=1,2
         do i=1,n
            t=real(i-1,FP_REAL)/real(n-1,FP_REAL)
            if (grid==2) t=t+0.2_FP_REAL*t*(1-t)
            x(i)=-0.5_FP_REAL+2*t
         end do
         if (grid==2) x=x(n:1:-1)
         do ik=1,size(orders)
            k=orders(ik)
            do degree=0,k
               do c=1,size(scales)
                  y=scales(c)*x**degree
                  saved_x=x; saved_y=y
                  status=curve%new_fit(x,y,smoothing=0.0_FP_REAL,order=k)
                  if (.not.FITPACK_SUCCESS(status)) error stop 'polynomial fit status'
                  if (any(x/=saved_x).or.any(y/=saved_y)) error stop 'changed source data'
                  fits=fits+1
                  do r=0,k
                     reference=0
                     if (r<=degree) then
                        scalar=scales(c)
                        do j=0,r-1
                           scalar=scalar*real(degree-j,FP_REAL)
                        end do
                        reference=scalar*targets**(degree-r)
                     end if
                     normalization=max(1.0_FP_REAL,maxval(abs(reference)))
                     values=curve%dfdx(targets,order=r,ierr=status)
                     if (.not.FITPACK_SUCCESS(status)) error stop 'vector derivative status'
                     if (size(values)/=33.or..not.all(ieee_is_finite(values))) &
                        error stop 'nonfinite vector derivative'
                     error=maxval(abs(values-reference))/normalization
                     if (error>1e-8_FP_REAL) error stop 'analytical vector derivative'
                     worst=max(worst,error); checks=checks+33
                     do i=1,33
                        scalar=curve%dfdx(targets(i),order=r,ierr=status)
                        if (.not.FITPACK_SUCCESS(status).or..not.ieee_is_finite(scalar)) &
                           error stop 'scalar derivative status'
                        error=abs(scalar-reference(i))/normalization
                        if (error>1e-8_FP_REAL) error stop 'analytical scalar derivative'
                        worst=max(worst,error); checks=checks+1
                     end do
                  end do
               end do
            end do
         end do
      end do
      deallocate(x,y,saved_x,saved_y)
   end do
   call curve%destroy()
   if (curve%m/=0.or.allocated(curve%x).or.allocated(curve%y).or.allocated(curve%t)) &
      error stop 'curve destruction'
   if (fits/=144.or.checks/=44352) error stop 'accounting'
   print '(a,i0,a,i0)', 'Polynomial fits: ',fits,'; derivative/value references: ',checks
   print '(a)', 'Degrees 1/3/5; uniform and reversed nonuniform data; scalar/vector overloads.'
   print '(a,es12.4)', 'Maximum normalized derivative/value error: ',worst
   print '(a)', 'PASS fitpack-polynomial-derivatives'
end program
