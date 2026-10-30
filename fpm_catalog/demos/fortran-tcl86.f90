program main
   use, intrinsic :: iso_c_binding, only: c_ptr, c_associated
   use tcl, only: tcl_create_interp, tcl_delete_interp, tcl_eval_ex, tcl_get_string_result, TCL_OK
   implicit none
   type(c_ptr) :: interp
   character(len=:), allocatable :: result
   integer :: status, value

   interp = tcl_create_interp()
   if (.not. c_associated(interp)) error stop 'interpreter creation failed'
   status = tcl_eval_ex(interp, 'set total 0; foreach x {1 2 3 4 5} {incr total [expr {$x*$x}]}; set total')
   if (status /= TCL_OK) error stop 'Tcl script failed'
   result = tcl_get_string_result(interp)
   read(result, *, iostat=status) value
   if (status /= 0) error stop 'Tcl returned a noninteger result'
   if (value /= sum([1, 2, 3, 4, 5]**2)) error stop 'Tcl calculation mismatch'
   print '(a,a)', 'Tcl sum of squares of 1 through 5: ', result
   call tcl_delete_interp(interp)
   print *, 'PASS fortran-tcl86'
end program
