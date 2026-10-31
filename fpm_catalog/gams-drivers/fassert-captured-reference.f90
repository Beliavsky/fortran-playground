! Independent API consumer; MIT: licenses/products-status-drivers-MIT.txt.
program captured_assertions
   use fassert, only: assert_equal,assert_approx_equal,expect_equal,expect_approx_equal
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   real(real64), parameter :: deltas(*) = [-.75_real64,-.5_real64,-.25_real64,0._real64, &
      .25_real64,.5_real64,.75_real64], tol = .5_real64
   real(real64) :: values(3)
   character(:), allocatable :: message
   logical :: passed,expected
   integer :: i,captured
   captured = 0
   call assert_equal(3*7,21,'integer arithmetic')
   call assert_equal([1,4,9],[1,4,9],'integer squares')
   call assert_approx_equal(sqrt(2._real64)**2,2._real64,'numerical assertion',tolerance=1.e-12_real64)
   call expect_equal(7,7,'equal scalar',passed,output_message=message)
   call validate(passed,.true.,message,'equal scalar')
   call expect_equal(7,8,'unequal scalar',passed,output_message=message)
   call validate(passed,.false.,message,'unequal scalar')
   call expect_equal([1,4,9],[1,4,9],'equal vector',passed,output_message=message)
   call validate(passed,.true.,message,'equal vector')
   call expect_equal([1,4,8],[1,4,9],'unequal vector',passed,output_message=message)
   call validate(passed,.false.,message,'unequal vector')
   do i = 1,size(deltas)
      expected = abs(deltas(i)) <= tol
      call expect_approx_equal(10._real64+deltas(i),10._real64,'tolerance window',passed, &
         tolerance=tol,output_message=message)
      call validate(passed,expected,message,'tolerance window')
   end do
   values = [1._real64,2._real64,3.25_real64]
   call expect_approx_equal(values,[1._real64,2._real64,3._real64],'vector tolerance boundary',passed, &
      tolerance=.25_real64,output_message=message)
   call validate(passed,.true.,message,'vector tolerance boundary')
   values(3) = 3.5_real64
   call expect_approx_equal(values,[1._real64,2._real64,3._real64],'vector outside tolerance',passed, &
      tolerance=.25_real64,output_message=message)
   call validate(passed,.false.,message,'vector outside tolerance')
   if (captured /= 13) error stop 'captured comparison count'
   print '(a)', 'Three positive assertions and 13 captured comparisons checked.'
   print '(a)', 'Scalar/vector mismatches and both exact tolerance boundaries were detected without stopping.'
   print '(a)', 'PASS fassert-captured-reference'
contains
   subroutine validate(actual,expected,text,label)
      logical, intent(in) :: actual,expected
      character(*), intent(in) :: text,label
      if (actual .neqv. expected) error stop 'independent comparison truth value'
      if (index(text,label) == 0) error stop 'missing comparison label'
      if (expected) then
         if (index(text,'PASSED:') == 0) error stop 'success diagnostic'
      else
         if (index(text,'FAILED:') == 0) error stop 'failure diagnostic'
      end if
      captured = captured+1
   end subroutine validate
end program captured_assertions
