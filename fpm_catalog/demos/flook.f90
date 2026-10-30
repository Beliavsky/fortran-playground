program main
   use flook
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(luaState), target :: state
   type(luaTbl) :: table
   integer :: status, total
   real(real64) :: answer
   character(256) :: message
   call lua_init(state)
   ! Load a Lua chunk before accessing its global tables, as in the author examples.
   call lua_run(state, code='parameters = {}', error=status, message=message)
   if (status /= 0) error stop 'Lua initialization failed'
   table = lua_table(state, 'parameters')
   call lua_set(table, 'alpha', 2.5_real64)
   call lua_set(table, 'beta', -1.0_real64)
   call lua_set(table, 'n', 6)
   call lua_close(table)
   call lua_run(state, code='results = {answer=parameters.alpha*parameters.n+parameters.beta,total=0}; '// &
      'for i=1,parameters.n do results.total=results.total+i end', error=status, message=message)
   if (status /= 0) then
      print '(a)', trim(message)
      error stop 'Lua script failed'
   end if
   table = lua_table(state, 'results')
   answer = -huge(answer)
   total = -1
   call lua_get(table, 'answer', answer)
   call lua_get(table, 'total', total)
   call lua_close(table)
   call lua_close(state)
   if (.not. ieee_is_finite(answer)) error stop 'Nonfinite Lua result'
   if (abs(answer-14.0_real64) > 1.0e-12_real64 .or. total /= 21) error stop 'Lua result mismatch'
   print '(a,f8.3)', 'Lua computed alpha*n + beta: ', answer
   print '(a,i0)', 'Lua computed sum from 1 to n: ', total
   print '(a)', 'PASS flook'
end program main
