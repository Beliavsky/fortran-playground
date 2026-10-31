! Independent API consumer; MIT: licenses/io-bounds-drivers-MIT.txt.
program bounds_reference
   use, intrinsic :: iso_fortran_env, only: sp => real32,dp => real64
   use ErrorCriteriaModule, only: ErrorCriteria
   use ErrorInstanceModule, only: ErrorInstance
   implicit none
   type(ErrorCriteria) :: handler
   type(ErrorInstance) :: problem
   real(sp) :: single(11),s
   real(dp) :: double(11),d
   integer :: i,cases,rejections
   call handler%init(bashColors=.false.)
   cases = 0
   rejections = 0
   do i = -4,4
      problem = handler%limit(i,-2,2,message='bounded input',traceMessage='check_data')
      call check(i >= -2 .and. i <= 2)
      problem = handler%limit(i,lbound=-2,message='bounded input',traceMessage='check_data')
      call check(i >= -2)
      problem = handler%limit(i,ubound=2,message='bounded input',traceMessage='check_data')
      call check(i <= 2)
   end do
   single(:7) = [(-3._sp+real(i,sp),i=0,6)]
   double(:7) = [(-3._dp+real(i,dp),i=0,6)]
   single(8:) = [nearest(-2._sp,-1._sp),nearest(-2._sp,1._sp),nearest(2._sp,-1._sp),nearest(2._sp,1._sp)]
   double(8:) = [nearest(-2._dp,-1._dp),nearest(-2._dp,1._dp),nearest(2._dp,-1._dp),nearest(2._dp,1._dp)]
   do i = 1,11
      s = single(i)
      d = double(i)
      problem = handler%limit(s,-2._sp,2._sp,message='bounded input',traceMessage='check_data')
      call check(s >= -2 .and. s <= 2)
      problem = handler%limit(s,lbound=-2._sp,message='bounded input',traceMessage='check_data')
      call check(s >= -2)
      problem = handler%limit(s,ubound=2._sp,message='bounded input',traceMessage='check_data')
      call check(s <= 2)
      problem = handler%limit(d,-2._dp,2._dp,message='bounded input',traceMessage='check_data')
      call check(d >= -2 .and. d <= 2)
      problem = handler%limit(d,lbound=-2._dp,message='bounded input',traceMessage='check_data')
      call check(d >= -2)
      problem = handler%limit(d,ubound=2._dp,message='bounded input',traceMessage='check_data')
      call check(d <= 2)
   end do
   do i = -1,1
      problem = handler%limit(i,0,0,message='bounded input',traceMessage='check_data')
      call check(i == 0)
      s = real(i,sp)*epsilon(1._sp)
      problem = handler%limit(s,0._sp,0._sp,message='bounded input',traceMessage='check_data')
      call check(s == 0)
      d = real(i,dp)*epsilon(1._dp)
      problem = handler%limit(d,0._dp,0._dp,message='bounded input',traceMessage='check_data')
      call check(d == 0)
   end do
   if (cases /= 102 .or. rejections /= 30) error stop 'bounds case count'
   print '(a)', '102 integer/real32/real64 bounds checks; 30 expected rejections.'
   print '(a)', 'Inclusive endpoints, nearest inside/outside floats, one-sided and equal bounds checked.'
   print '(a)', 'Expected failures retain code 105, the custom message and one application trace.'
   print '(a)', 'PASS error-bounds-reference'
contains
   subroutine check(accepted)
      logical, intent(in) :: accepted
      if (problem%isError() .eqv. accepted) error stop 'native comparison reference'
      if (accepted) then
         if (problem%code /= 0) error stop 'success code'
      else
         if (problem%code /= 105) error stop 'bounds failure code'
         if (index(problem%message,'bounded input') /= 1) error stop 'bounds custom message'
         if (.not. allocated(problem%trace)) error stop 'missing bounds trace'
         if (size(problem%trace) /= 1) error stop 'bounds trace size'
         if (trim(problem%trace(1)) /= 'check_data') error stop 'bounds trace content'
         rejections = rejections+1
      end if
      cases = cases+1
   end subroutine check
end program bounds_reference
