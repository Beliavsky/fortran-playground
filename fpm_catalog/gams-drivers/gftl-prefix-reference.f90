! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   implicit none
   integer :: t
   do t=1,12
      call fixture(t)
   end do
   print '(a)', '12 vectors of 96 integers; 55,872 exact prefix values and 1,152 closed-form sums'
   print '(a)', 'PASS gftl-prefix-reference'
contains
   subroutine fixture(t)
      use playground_gftl, only: IntegerVector
      integer,intent(in) :: t
      type(IntegerVector) :: vector
      integer :: i,j,status,total
      vector=IntegerVector()
      do i=1,96
         call vector%push_back(t*i-101,rc=status)
         if(status/=0.or.vector%size()/=i) error stop 'Vector append'
         total=0
         do j=i,1,-1
            if(vector%at(j)/=t*j-101) error stop 'Prefix oracle'
            total=total+vector%at(j)
         end do
         if(total/=t*i*(i+1)/2-101*i) error stop 'Closed-form prefix sum'
      end do
   end subroutine
end program
