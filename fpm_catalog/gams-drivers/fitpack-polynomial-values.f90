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
                  reference=scales(c)*targets**degree
                  values=curve%eval(targets,status)
                  if (.not.FITPACK_SUCCESS(status)) error stop 'vector evaluation status'
                  if (size(values)/=33.or..not.all(ieee_is_finite(values))) error stop 'vector values'
                  normalization=max(1.0_FP_REAL,maxval(abs(reference)))
                  error=maxval(abs(values-reference))/normalization
                  if (error>5e-12_FP_REAL) error stop 'vector polynomial reference'
                  worst=max(worst,error); checks=checks+33
                  do i=1,33
                     scalar=curve%eval(targets(i),status)
                     if (.not.FITPACK_SUCCESS(status).or..not.ieee_is_finite(scalar)) &
                        error stop 'scalar evaluation status'
                     error=abs(scalar-reference(i))/normalization
                     if (error>5e-12_FP_REAL) error stop 'scalar polynomial reference'
                     worst=max(worst,error); checks=checks+1
                  end do
                  ! Vector evaluation requires sorted targets, independently of source order.
                  if (grid==2) then
                     nodes=curve%eval(x(n:1:-1),status)
                     error=maxval(abs(nodes-y(n:1:-1)))
                  else
                     nodes=curve%eval(x,status)
                     error=maxval(abs(nodes-y))
                  end if
                  if (.not.FITPACK_SUCCESS(status).or..not.all(ieee_is_finite(nodes))) &
                     error stop 'source node evaluation'
                  error=error/max(1.0_FP_REAL,maxval(abs(y)))
                  if (error>5e-12_FP_REAL) error stop 'source node interpolation'
                  worst=max(worst,error); checks=checks+n
               end do
            end do
         end do
      end do
      deallocate(x,y,saved_x,saved_y)
   end do
   call curve%destroy()
   if (curve%m/=0.or.allocated(curve%x).or.allocated(curve%y).or.allocated(curve%t)) &
      error stop 'curve destruction'
   if (fits/=144.or.checks/=11016) error stop 'accounting'
   print '(a,i0,a,i0)', 'Polynomial fits: ',fits,'; value references: ',checks
   print '(a)', 'Degrees 1/3/5; uniform and reversed nonuniform data; scalar/vector overloads.'
   print '(a,es12.4)', 'Maximum normalized value error: ',worst
   print '(a)', 'PASS fitpack-polynomial-values'
end program
