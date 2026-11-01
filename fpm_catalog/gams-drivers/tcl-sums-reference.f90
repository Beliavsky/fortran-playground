! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   use iso_c_binding, only: c_ptr,c_associated
   use tcl, only: tcl_create_interp,tcl_delete_interp,tcl_eval_ex,tcl_get_string_result,TCL_OK
   implicit none
   type(c_ptr) :: interp
   character(20) :: number
   character(:),allocatable :: script,result
   integer :: n,status,value
   interp=tcl_create_interp()
   if(.not.c_associated(interp)) error stop 'Tcl interpreter'
   do n=0,64
      write(number,'(i0)') n
      script='set total 0; for {set i 1} {$i <= '//trim(number)// &
         '} {incr i} {incr total [expr {$i*$i}]}; set total'
      status=tcl_eval_ex(interp,script)
      if(status/=TCL_OK) error stop 'Tcl sum evaluation'
      result=tcl_get_string_result(interp)
      read(result,*,iostat=status) value
      if(status/=0.or.value/=n*(n+1)*(2*n+1)/6) error stop 'Closed-form sum of squares'
   end do
   status=tcl_eval_ex(interp,'expr {1 + }')
   if(status==TCL_OK) error stop 'Malformed expression accepted'
   result=tcl_get_string_result(interp)
   if(len(result)==0) error stop 'Missing error text'
   status=tcl_eval_ex(interp,'expr {7*8}')
   if(status/=TCL_OK) error stop 'Tcl recovery'
   result=tcl_get_string_result(interp)
   if(result/='56') error stop 'Recovery value'
   call tcl_delete_interp(interp)
   print '(a)', '65 Tcl finite-sum references, syntax rejection and successful interpreter recovery'
   print '(a)', 'PASS tcl-sums-reference'
end program
