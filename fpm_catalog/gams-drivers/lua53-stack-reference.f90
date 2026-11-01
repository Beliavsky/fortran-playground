! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use iso_c_binding, only: c_ptr,c_associated
   use lua
   implicit none
   type(c_ptr) :: state
   integer :: status,i
   integer(kind=lua_integer) :: actual
   real(kind=lua_number) :: x,y
   state=lual_newstate()
   if(.not.c_associated(state)) error stop 'Lua state'
   call lual_openlibs(state)
   status=lual_loadstring(state,'function calculate(n,x) return n*n-3*n+7, 2.5*x-0.125 end')
   if(status/=0) error stop 'Lua load'
   status=lua_pcall(state,0,0,0)
   if(status/=0) error stop 'Lua define'
   do i=-64,64
      if(lua_gettop(state)/=0) error stop 'Initial stack depth'
      status=lua_getglobal(state,'calculate')
      if(lua_isfunction(state,-1)/=1) error stop 'Not callable'
      call lua_pushinteger(state,int(i,lua_integer))
      x=real(i,lua_number)/8
      call lua_pushnumber(state,x)
      status=lua_pcall(state,2,2,0)
      if(status/=0 .or. lua_gettop(state)/=2) error stop 'Call/stack'
      actual=lua_tointeger(state,-2)
      y=lua_tonumber(state,-1)
      if(actual/=i*i-3*i+7) error stop 'Integer polynomial'
      if(y/=real(20*i-8,lua_number)/64) error stop 'Dyadic affine value'
      call lua_pop(state,2)
      if(lua_gettop(state)/=0) error stop 'Stack cleanup'
   end do
   status=lual_loadstring(state,'function broken(')
   if(status==0) error stop 'Syntax accepted'
   call lua_pop(state,1)
   if(lua_gettop(state)/=0) error stop 'Error stack cleanup'
   call lua_close(state)
   print '(a)', '129 Lua calls; 258 exact numeric references, stack balance and syntax rejection'
   print '(a)', 'PASS lua53-stack-reference'
end program
