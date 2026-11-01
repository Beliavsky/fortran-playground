! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   use julienne_m, only: test_diagnosis_t,operator(.equalsExpected.), &
      operator(.approximates.),operator(.within.),operator(//)
   implicit none
   type(test_diagnosis_t) :: diagnosis
   character(:),allocatable :: message
   integer :: i,j,k,checks
   real :: actual,expected,tolerance
   checks=0
   do i=-8,8
      do j=-8,8
         diagnosis=(i.equalsExpected.j)
         if(diagnosis%test_passed().neqv.(i==j)) error stop 'Integer diagnosis truth table'
         checks=checks+1
      end do
   end do
   do i=-8,8
      expected=real(i)/4
      do j=-4,4
         actual=expected+real(j)/16
         do k=0,4
            tolerance=real(k)/16
            diagnosis=(actual.approximates.expected.within.tolerance)
            if(diagnosis%test_passed().neqv.(abs(j)<=k)) error stop 'Dyadic tolerance boundary'
            checks=checks+1
         end do
      end do
   end do
   diagnosis=(1.equalsExpected.2)//' expected fixture failure'
   if(diagnosis%test_passed()) error stop 'Failure changed to success'
   message=diagnosis%diagnostics_string()
   if(index(message,'expected fixture failure')==0) error stop 'Diagnostic annotation'
   print '(a,i0)', 'Exact equality and inclusive absolute-tolerance truth-table references: ',checks
   print '(a)', 'PASS julienne-diagnosis-reference'
end program
