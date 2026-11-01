! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use flook
   implicit none
   type(luaState),target :: state
   type(luaTbl) :: table
   integer :: n,k,status,total,count
   real(real64) :: alpha,beta,answer,expected
   character(:),allocatable :: message
   call lua_init(state)
   count=0
   do n=0,16
      do k=-4,4
         alpha=real(k,real64)/8
         beta=real(n-8,real64)/4
         call lua_run(state,code='parameters = {}',error=status,message=message)
         if(status/=0) error stop 'Lua table creation'
         table=lua_table(state,'parameters')
         call lua_set(table,'alpha',alpha)
         call lua_set(table,'beta',beta)
         call lua_set(table,'n',n)
         call lua_close(table)
         call lua_run(state,code='results = {answer=parameters.alpha*parameters.n+parameters.beta,total=0}; '// &
            'for i=1,parameters.n do results.total=results.total+i end',error=status,message=message)
         if(status/=0) error stop 'Lua computation'
         table=lua_table(state,'results')
         call lua_get(table,'answer',answer)
         call lua_get(table,'total',total)
         call lua_close(table)
         expected=real(k*n+2*n-16,real64)/8
         if(answer/=expected .or. total/=n*(n+1)/2) error stop 'Lua analytic reference'
         count=count+2
      end do
   end do
   call lua_close(state)
   print '(a,i0)', '153 Lua table traces; exact affine and triangular-sum references: ',count
   print '(a)', 'PASS flook-table-reference'
end program
