! Evaluate a Lua function with integer and real results, without external files.
program main
   use, intrinsic :: iso_c_binding, only: c_ptr, c_associated
   use lua
   implicit none
   type(c_ptr) :: state
   integer :: status, i
   integer(kind=lua_integer) :: square
   real(kind=lua_number) :: root
   state = lual_newstate()
   if (.not. c_associated(state)) error stop 'Lua allocation failed'
   call lual_openlibs(state)
   status = lual_loadstring(state, 'function calculate(x) return x*x, math.sqrt(x) end')
   if (status /= LUA_OK) error stop 'Lua parsing failed'
   status = lua_pcall(state, 0, 0, 0)
   if (status /= LUA_OK) error stop 'Lua definition failed'
   do i = 1, 4
      status = lua_getglobal(state, 'calculate')
      if (lua_isfunction(state, -1) /= 1) error stop 'Lua function missing'
      call lua_pushinteger(state, int(i, kind=lua_integer))
      status = lua_pcall(state, 1, 2, 0)
      if (status /= LUA_OK) error stop 'Lua call failed'
      square = lua_tointeger(state, -2)
      root = lua_tonumber(state, -1)
      if (square /= i*i) error stop 'integer result mismatch'
      if (abs(root - sqrt(real(i, lua_number))) > 1.0e-12_lua_number) error stop 'real result mismatch'
      print '(i2,a,i3,a,f12.8)', i, ': square = ', square, ', square root = ', root
      call lua_pop(state, 2)
      if (lua_gettop(state) /= 0) error stop 'Lua stack was not cleared'
   end do
   call lua_close(state)
   print '(a)', 'PASS fortran-lua53'
end program main
