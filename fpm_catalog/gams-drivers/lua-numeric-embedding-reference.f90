! Independent API consumer; MIT: licenses/delay-embedding-drivers-MIT.txt.
program numeric_embedding_reference
   use, intrinsic :: iso_c_binding, only: c_associated
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use lua
   implicit none
   character(*), parameter :: source = &
      'function fact(n) if n<0 then error("negative factorial") end local p=1 '// &
      'for k=2,n do p=p*k end return p end '// &
      'function squares(n) local s=0 for k=1,n do s=s+k*k end return s end '// &
      'function polynomial(n) return (n-3)*(n+2) end '// &
      'function norm(a,b) return math.sqrt(a*a+b*b) end'
   real(lua_number), parameter :: triples(3,5) = reshape([3.d0,4.d0,5.d0,5.d0,12.d0,13.d0, &
      8.d0,15.d0,17.d0,-3.d0,4.d0,5.d0,0.d0,0.d0,0.d0],[3,5])
   type(c_ptr) :: state
   integer(lua_integer) :: factorial,n
   real(lua_number) :: answer,max_real_error
   character(:), allocatable :: message
   integer :: status,i,kind,integer_calls,real_calls
   state = lual_newstate()
   if (.not. c_associated(state)) error stop 'Lua state creation'
   call lual_openlibs(state)
   status = lual_loadstring(state,source)
   if (status /= LUA_OK) error stop 'numeric script load'
   status = lua_pcall(state,0,0,0)
   if (status /= LUA_OK) error stop 'numeric script definition'
   if (lua_gettop(state) /= 0) error stop 'definition stack balance'
   integer_calls = 0
   real_calls = 0
   max_real_error = 0.d0
   factorial = 1_lua_integer
   do i = 0,20
      n = int(i,lua_integer)
      if (i > 0) factorial = factorial*n
      call integer_case('fact',n,factorial)
   end do
   do i = 0,64
      n = int(i,lua_integer)
      call integer_case('squares',n,n*(n+1)*(2*n+1)/6)
   end do
   do i = -20,20
      n = int(i,lua_integer)
      call integer_case('polynomial',n,(n-3)*(n+2))
   end do
   do i = 1,5
      kind = lua_getglobal(state,'norm')
      if (kind /= LUA_TFUNCTION) error stop 'Lua real function type'
      call lua_pushnumber(state,triples(1,i))
      call lua_pushnumber(state,triples(2,i))
      status = lua_pcall(state,2,1,0)
      if (status /= LUA_OK .or. lua_gettop(state) /= 1) error stop 'Lua real return/stack'
      if (lua_isnumber(state,-1) == 0) error stop 'Lua real result type'
      answer = lua_tonumber(state,-1)
      if (.not. ieee_is_finite(answer)) error stop 'nonfinite embedded result'
      max_real_error = max(max_real_error,abs(answer-triples(3,i)))
      if (abs(answer-triples(3,i)) > 1.d-12) error stop 'known Pythagorean norm'
      call lua_settop(state,0)
      real_calls = real_calls+1
   end do
   kind = lua_getglobal(state,'fact')
   call lua_pushinteger(state,-1_lua_integer)
   status = lua_pcall(state,1,1,0)
   if (status /= LUA_ERRRUN .or. lua_gettop(state) /= 1) error stop 'expected runtime error'
   message = lua_tostring(state,-1)
   if (.not. allocated(message)) error stop 'missing runtime diagnostic'
   if (index(message,'negative factorial') == 0) error stop 'runtime diagnostic content'
   call lua_settop(state,0)
   status = lual_loadstring(state,'function broken(')
   if (status /= LUA_ERRSYNTAX .or. lua_gettop(state) /= 1) error stop 'expected syntax error'
   message = lua_tostring(state,-1)
   if (.not. allocated(message)) error stop 'missing syntax diagnostic'
   if (len_trim(message) == 0) error stop 'empty syntax diagnostic'
   call lua_settop(state,0)
   call integer_case('fact',6_lua_integer,720_lua_integer)
   if (lua_gettop(state) /= 0) error stop 'final stack balance'
   call lua_close(state)
   if (integer_calls /= 128 .or. real_calls /= 5) error stop 'embedding case count'
   print '(a)', '128 exact integer calls: factorials through 20!, sums of squares, signed polynomials and error recovery.'
   print '(a,es12.4)', 'Five real Pythagorean norm calls, maximum absolute error: ',max_real_error
   print '(a)', 'Return types, stack balance, expected runtime/syntax diagnostics and subsequent state reuse checked.'
   print '(a)', 'PASS lua-numeric-embedding-reference'
contains
   subroutine integer_case(name,value,expected)
      character(*), intent(in) :: name
      integer(lua_integer), intent(in) :: value,expected
      if (lua_gettop(state) /= 0) error stop 'integer call initial stack'
      kind = lua_getglobal(state,name)
      if (kind /= LUA_TFUNCTION) error stop 'Lua integer function type'
      call lua_pushinteger(state,value)
      status = lua_pcall(state,1,1,0)
      if (status /= LUA_OK .or. lua_gettop(state) /= 1) error stop 'Lua integer return/stack'
      if (lua_isinteger(state,-1) == 0) error stop 'Lua integer result type'
      if (lua_tointeger(state,-1) /= expected) error stop 'independent integer reference'
      call lua_settop(state,0)
      integer_calls = integer_calls+1
   end subroutine integer_case
end program numeric_embedding_reference
