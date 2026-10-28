program main
   use iso_varying_string, only: varying_string,var_str,char,len,index,insert,remove,operator(//)
   implicit none
   type(varying_string) :: text
   text=var_str('Fortran')//' playground'
   if (len(text)/=18.or.index(text,'playground')/=9) error stop
   print '(a)', char(text)
   text=insert(text,8,':')
   if (char(text)/='Fortran: playground') error stop 'Insertion failed'
   print '(a)', char(text)
   text=remove(text,8,8)
   if (char(text)/='Fortran playground') error stop 'Removal failed'
   print '(a)', char(text)
   print *, 'PASS iso_varying_string'
end program
