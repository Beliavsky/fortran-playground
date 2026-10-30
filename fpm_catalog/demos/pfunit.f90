! Plain Fortran serial pFUnit example: no annotation preprocessor is needed.
! This catalog configuration supports assertion ranks 0, 1 and 2.
module playground_checks
   use iso_fortran_env, only: real64
   use FUnit, only: assertEqual, assertTrue
   implicit none
contains
   subroutine scalar_checks()
      call assertEqual(4,2+2)
      call assertTrue(sqrt(2.0_real64)>1.0_real64)
      call assertEqual(2.0_real64,sqrt(2.0_real64)**2,tolerance=1.0e-12_real64)
   end subroutine scalar_checks
   subroutine vector_checks()
      real(real64) :: a(3)=[1.0_real64,2.0_real64,3.0_real64]
      call assertEqual([1.0_real64,4.0_real64,9.0_real64],a*a,tolerance=1.0e-12_real64)
   end subroutine vector_checks
   subroutine matrix_checks()
      real(real64) :: a(2,2), identity(2,2)
      a=reshape([1.0_real64,2.0_real64,3.0_real64,4.0_real64],[2,2])
      identity=reshape([1.0_real64,0.0_real64,0.0_real64,1.0_real64],[2,2])
      call assertEqual(a,matmul(a,identity),tolerance=1.0e-12_real64)
   end subroutine matrix_checks
end module playground_checks

program main
   use FUnit, only: TestSuite, TestMethod, TestRunner, TestResult, SerialContext
   use playground_checks
   implicit none
   type(TestSuite) :: suite
   type(TestRunner) :: runner
   type(TestResult) :: result
   type(SerialContext) :: context
   suite=TestSuite('Playground')
   call suite%addTest(TestMethod('scalar arithmetic',scalar_checks))
   call suite%addTest(TestMethod('vector squares',vector_checks))
   call suite%addTest(TestMethod('matrix identity',matrix_checks))
   runner=TestRunner()
   result=runner%run(suite,context)
   if (.not.result%wasSuccessful()) error stop 'pFUnit checks failed'
   if (result%runCount()/=3 .or. result%failureCount()/=0 .or. result%errorCount()/=0) &
      error stop 'Unexpected test counts'
   print '(a,i0)', 'Verified test cases: ',result%runCount()
   print '(a)', 'PASS pfunit'
end program main
