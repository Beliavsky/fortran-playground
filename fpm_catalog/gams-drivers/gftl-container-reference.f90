! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   implicit none
   integer :: trial
   do trial=1,12
      call fixture(trial)
   end do
   print '(a)', '12 vector/map traces of 64 insertions; every prefix and reverse-order lookup checked'
   print '(a)', 'PASS gftl-container-reference'
contains
   subroutine fixture(t)
      use iso_fortran_env, only: int32,real64
      use gFTL1_Integer32Vector
      use gFTL1_Integer32Real64Map
      integer,intent(in) :: t
      type(Integer32Vector) :: vector
      type(Integer32Real64Map) :: map
      integer(int32) :: i,j,key
      integer :: count
      real(real64) :: value
      vector=Integer32Vector()
      map=Integer32Real64Map()
      do i=1,64
         key=3*i-100
         call vector%push_back(key)
         value=real(t*i-31,real64)/8
         call map%insert(key,value)
         if(vector%size()/=i.or.map%size()/=i) error stop 'Container size'
         count=0
         do j=i,1,-1
            if(vector%at(j)/=3*j-100) error stop 'Vector prefix'
            if(map%at(3*j-100)/=real(t*j-31,real64)/8) error stop 'Map prefix'
            count=count+1
         end do
         if(count/=i) error stop 'Reference count'
      end do
   end subroutine
end program
