module numerical_specification
   use veggies, only: result_t,assert_equals
   implicit none
contains
   pure double precision function simpson(values,h) result(integral)
      double precision,intent(in)::values(3),h
      integral=h*(values(1)+4*values(2)+values(3))/3
   end function simpson
   function constant_case() result(check)
      type(result_t)::check
      check=assert_equals(6.d0,simpson([3.d0,3.d0,3.d0],1.d0))
   end function constant_case
   function linear_case() result(check)
      type(result_t)::check
      check=assert_equals(2.d0,simpson([0.d0,1.d0,2.d0],1.d0))
   end function linear_case
   function quadratic_case() result(check)
      type(result_t)::check
      check=assert_equals(8.d0/3,simpson([0.d0,1.d0,4.d0],1.d0))
   end function quadratic_case
end module numerical_specification

program run_specification
   use numerical_specification
   use veggies, only: test_item_t,describe,it,run_tests
   implicit none
   type(test_item_t)::tests
   tests=describe('Simpson integration on [0,2]',[ &
      it('integrates a constant exactly',constant_case), &
      it('integrates a linear function exactly',linear_case), &
      it('integrates a quadratic exactly',quadratic_case)])
   if(.not.run_tests(tests)) error stop 'Numerical specification failed'
   print *, 'PASS veggies'
end program run_specification
