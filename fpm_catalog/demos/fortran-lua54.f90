! Adapted from the author's in-memory string example; no script file is needed.
program main
   use, intrinsic :: iso_c_binding, only: c_associated
   use lua
   implicit none
   type(c_ptr) :: state
   integer :: status, kind
   integer(lua_integer) :: answer
   state = lual_newstate()
   if (.not. c_associated(state)) error stop 'Cannot create Lua state'
   call lual_openlibs(state)
   status = lual_loadstring(state, 'function square_plus_one(x) return x*x+1 end')
   if (status /= LUA_OK) error stop 'Lua source did not load'
   status = lua_pcall(state, 0, 0, 0)
   if (status /= LUA_OK) error stop 'Lua definition failed'
   kind = lua_getglobal(state, 'square_plus_one')
   if (kind /= LUA_TFUNCTION) error stop 'Expected a Lua function'
   call lua_pushinteger(state, 6_lua_integer)
   status = lua_pcall(state, 1, 1, 0)
   if (status /= LUA_OK) error stop 'Lua call failed'
   answer = lua_tointeger(state, -1)
   call lua_close(state)
   print '(a,i0)', 'Lua square_plus_one(6) = ', answer
   if (answer /= 37_lua_integer) error stop 'Incorrect Lua result'
   print '(a)', 'PASS fortran-lua54'
end program main
