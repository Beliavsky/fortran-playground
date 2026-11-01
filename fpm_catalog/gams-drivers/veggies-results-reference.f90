! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
module checked_specification
   use veggies, only: result_t,assert_equals
   implicit none
contains
   function integer_case() result(check)
      type(result_t) :: check
      integer :: n,i
      check=assert_equals(0,0)
      do n=1,64
         check=check.and.assert_equals(n*(n+1)/2,sum([(i,i=1,n)]))
      end do
   end function
   function exact_real_case() result(check)
      type(result_t) :: check
      check=assert_equals(2.d0,0.25d0*8)
   end function
end module
program main
   use checked_specification
   use veggies, only: test_item_t,describe,it,run_tests
   implicit none
   type(test_item_t) :: tests
   type(result_t) :: check,combined
   integer :: i,j,failures
   do i=-8,8
      combined=assert_equals(i,i)
      failures=0
      do j=-8,8
         check=assert_equals(i,j)
         if(check%passed().neqv.(i==j)) error stop 'Equality truth table'
         if(check%num_asserts()/=1) error stop 'Assertion count'
         if(i/=j) failures=failures+1
         combined=combined.and.check
      end do
      if(combined%num_asserts()/=18) error stop 'Combined count'
      if(combined%num_failing_asserts()/=failures) error stop 'Failure count'
      if(combined%passed()) error stop 'Mixed result accepted'
   end do
   tests=describe('Checked framework consumers',[it('integer references',integer_case), &
      it('exact binary real',exact_real_case)])
   if(.not.run_tests(tests)) error stop 'Framework run'
   print '(a)', '289 equality outcomes and 17 mixed-result counts; two passing specification cases'
   print '(a)', 'PASS veggies-results-reference'
end program
