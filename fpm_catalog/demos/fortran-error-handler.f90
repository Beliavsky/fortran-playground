! Recoverable diagnostics: validate values and retain a useful application trace.
program main
   use ErrorCriteriaModule
   use ErrorInstanceModule
   use ResultModule
   implicit none
   type(ErrorCriteria) :: handler
   type(ErrorInstance) :: problem
   type(Result0D) :: checked
   call handler%init(errors=[ErrorInstance(code=200, message='Demonstration warning; continuing.', &
      isCritical=.false.)], bashColors=.false.)
   problem = handler%limit(7,0,10)
   if (problem%isError()) error stop 'Valid input was rejected'
   checked = Result(data=7, errors=[problem])
   if (checked%hasError()) error stop 'Unexpected result error'
   print '(a,i0)', 'Accepted value: ', checked%getDataAsInteger()
   problem = handler%limit(12,0,10)
   if (.not. problem%isError() .or. problem%code /= 105) error stop 'Missing range error'
   call problem%addToTrace('read_input')
   call problem%addToTrace('validate_configuration')
   if (size(problem%trace) /= 2) error stop 'Missing application trace'
   print '(a,i0,2a)', 'Rejected value 12 with code ', problem%code, ': ', trim(problem%message)
   print '(a)', 'Trace: ' // trim(problem%trace(1)) // ' -> ' // trim(problem%trace(2))
   call handler%trigger(200)
   print '(a)', 'PASS fortran-error-handler'
end program main
