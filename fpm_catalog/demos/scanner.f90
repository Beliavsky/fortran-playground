program scan_configuration
   use scanner, only: textscanner
   use stdlib_string_type, only: string_type, assignment(=)
   implicit none
   type(textscanner)::scan
   type(string_type)::input
   character(*),parameter::record='steps=12;dt=0.25'
   character(len(record))::recovered
   integer::i,code,steps,separator,status
   real::dt
   input=record
   call scan%new(input)
   ! Reconstruct the complete record through the scanner API.
   do i=1,len(record)
      code=scan%current()
      if(code<0) error stop 'Unexpected end of text'
      recovered(i:i)=achar(code)
      if(i<len(record)) then
         code=scan%next()
         if(code<0) error stop 'Unexpected end while advancing'
      end if
   end do
   if(recovered/=record) error stop 'Text reconstruction mismatch'
   if(scan%next()/=-1) error stop 'Scanner advanced beyond the end'
   call scan%first()
   if(scan%prev()/=-1) error stop 'Scanner moved before the beginning'
   call scan%jump_to(iachar('='))
   if(scan%current()/=iachar('=')) error stop 'First equals not found'
   if(scan%peek()/=iachar('1')) error stop 'Peek mismatch'
   if(scan%current()/=iachar('=')) error stop 'Peek moved the cursor'
   separator=index(recovered,';')
   read(recovered(7:separator-1),*,iostat=status) steps
   if(status/=0) error stop 'Integer conversion failed'
   call scan%jump_to(iachar(';'))
   call scan%jump_to(iachar('='))
   if(scan%peek()/=iachar('0')) error stop 'Second field not found'
   read(recovered(separator+4:),*,iostat=status) dt
   if(status/=0) error stop 'Real conversion failed'
   if(steps/=12 .or. abs(dt-0.25)>epsilon(dt)) error stop 'Parsed values mismatch'
   print '(a)', 'Scanned: '//recovered
   print '(a,i0,a,f6.3)', 'steps=',steps,'  dt=',dt
   print '(a)', 'End boundaries and non-moving peek verified.'
   print *, 'PASS scanner'
end program scan_configuration
