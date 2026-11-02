! Independent MIT consumer; see licenses/integrals-tensors-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use linear_interpolation_module, only: linear_interp_4d
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(linear_interp_4d) :: interpolator
   real(wp) :: grid(4,4),data(4,4,4,4),saved(4,4,4,4),point(4),linear_square(4),answer,expected
   real(wp),parameter :: basegrid(4)=[-1._wp,-0.25_wp,0.5_wp,2._wp]
   integer :: indices(4),cell(4),i,j,index,query,mode,work,status,cases
   do j=1,4
      grid(:,j)=basegrid*real(j,wp)/2
   end do
   cases=0
   do mode=0,1
      do index=0,4**4-1
         work=index
         do j=1,4
            indices(j)=mod(work,4)+1; work=work/4; point(j)=grid(indices(j),j)
         end do
         data(indices(1),indices(2),indices(3),indices(4))=multiaffine(point)+real(mode,wp)*sum([(real(j,wp)*point(j)**2,j=1,4)])
      end do
      saved=data
      call interpolator%initialize(grid(:,1),grid(:,2),grid(:,3),grid(:,4),data,status)
      if(status/=0) error stop 'Tensor linear initialization'
      do index=0,3**4-1
         work=index
         do j=1,4
            cell(j)=mod(work,3)+1; work=work/3
         end do
         do query=0,3**4-1
            work=query
            do j=1,4
               i=mod(work,3); work=work/3
               point(j)=grid(cell(j),j)+real(i,wp)*(grid(cell(j)+1,j)-grid(cell(j),j))/2
               linear_square(j)=(grid(cell(j),j)+grid(cell(j)+1,j))*point(j) &
                  -grid(cell(j),j)*grid(cell(j)+1,j)
            end do
            expected=multiaffine(point)+real(mode,wp)*sum([(real(j,wp)*linear_square(j),j=1,4)])
            call interpolator%evaluate(point(1),point(2),point(3),point(4),answer,status)
            if(status/=0) error stop 'Tensor linear evaluation'
            call check(answer,expected); cases=cases+1
         end do
      end do
      if(any(data/=saved)) error stop 'Tensor data preservation'
      call interpolator%destroy()
   end do
   print '(a,i0)', 'Tensor linear node/interior/cell-boundary checks: ',cases
   print '(a)', 'PASS finterp-4d-cell-polynomials-reference'
contains
   function multiaffine(x) result(y)
      real(wp),intent(in) :: x(4)
      real(wp) :: y
      integer :: j
      y=1+sum([(real(j,wp)*x(j),j=1,4)])+product(x)+x(1)*x(2)-2*x(2)*x(3)
   end function
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
