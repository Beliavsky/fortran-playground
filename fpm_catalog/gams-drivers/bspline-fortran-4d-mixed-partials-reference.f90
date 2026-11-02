! Independent MIT consumer; see licenses/integrals-tensors-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use bspline_module, only: bspline_4d
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(bspline_4d) :: spline
   real(wp) :: grid(5,4),data(5,5,5,5),saved(5,5,5,5),point(4),answer,expected
   real(wp),parameter :: basegrid(5)=[-1._wp,-0.5_wp,0._wp,0.75_wp,2._wp]
   integer,parameter :: degrees(4,8)=reshape([ &
      0,0,0,0,3,0,0,0,0,3,0,0,0,0,3,0,0,0,0,3,1,1,1,1,2,1,0,0,0,1,2,0],[4,8])
   real(wp),parameter :: coefficients(8)=[1._wp,1._wp,2._wp,3._wp,4._wp,1._wp,2._wp,-1._wp]
   integer :: indices(4),derivative(4),index,query,mode,work,i,j,status,cases
   do j=1,4
      grid(:,j)=basegrid*real(j,wp)/2
   end do
   do index=0,5**4-1
      work=index
      do j=1,4
         indices(j)=mod(work,5)+1; work=work/5; point(j)=grid(indices(j),j)
      end do
      data(indices(1),indices(2),indices(3),indices(4))=1+sum([(real(j,wp)*point(j)**3,j=1,4)]) &
         +product(point)+2*point(1)**2*point(2)-point(2)*point(3)**2
   end do
   saved=data
   call spline%initialize(grid(:,1),grid(:,2),grid(:,3),grid(:,4),data,4,4,4,4,status)
   if(status/=0) error stop 'Tensor spline initialization'
   cases=0
   do query=0,4**4-1
      work=query
      do j=1,4
         i=mod(work,4); work=work/4
         point(j)=grid(1,j)+real(2*i+1,wp)*(grid(5,j)-grid(1,j))/8
      end do
      do mode=0,3**4-1
         work=mode
         do j=1,4
            derivative(j)=mod(work,3); work=work/3
         end do
         expected=polynomial_derivative(point,derivative)
         call spline%evaluate(point(1),point(2),point(3),point(4), &
            derivative(1),derivative(2),derivative(3),derivative(4),answer,status)
         if(status/=0) error stop 'Tensor spline evaluation'
         call check(answer,expected); cases=cases+1
      end do
   end do
   if(any(data/=saved)) error stop 'Spline data preservation'
   call spline%destroy()
   print '(a,i0)', 'Tensor cubic values and analytic mixed partial derivatives: ',cases
   print '(a)', 'PASS bspline-fortran-4d-mixed-partials-reference'
contains
   function polynomial_derivative(x,orders) result(y)
      real(wp),intent(in) :: x(4)
      integer,intent(in) :: orders(4)
      real(wp) :: y,term
      integer :: k,j,r,p
      y=0
      do k=1,8
         term=coefficients(k)
         do j=1,4
            p=degrees(j,k)
            if(orders(j)>p) then
               term=0; exit
            end if
            do r=0,orders(j)-1
               term=term*real(p-r,wp)
            end do
            term=term*x(j)**(p-orders(j))
         end do
         y=y+term
      end do
   end function
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>1.e-8_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
