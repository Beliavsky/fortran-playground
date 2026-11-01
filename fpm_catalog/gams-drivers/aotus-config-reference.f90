! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   implicit none
   integer :: t
   do t=1,32
      call fixture(t)
   end do
   print '(a)', '32 Lua configurations; exact computed scalar/table values and missing defaults'
   print '(a)', 'PASS aotus-config-reference'
contains
   subroutine fixture(t)
      use aotus_module, only: flu_State,open_config_file,close_config,aot_get_val,aoterr_Fatal,aoterr_NonExistent
      use aot_table_module, only: aot_table_open,aot_table_close,aot_table_length
      use flu_kinds_module, only: double_k
      integer,intent(in) :: t
      type(flu_State) :: state
      integer :: unit,status,steps,nx,ny,table,default_value
      real(double_k) :: scale
      open(newunit=unit,file='checked.lua',status='new')
      write(unit,'(a,i0)') 'n=',t
      write(unit,'(a)') 'steps=n*(n+1)/2', 'scale=(n-17)/8', 'mesh={nx=n+2,ny=3*n-4}'
      close(unit)
      call open_config_file(L=state,filename='checked.lua',ErrCode=status)
      if(status/=0) error stop 'Configuration load'
      call aot_get_val(L=state,key='steps',val=steps,ErrCode=status)
      if(btest(status,aoterr_Fatal).or.steps/=t*(t+1)/2) error stop 'Computed integer'
      call aot_get_val(L=state,key='scale',val=scale,ErrCode=status)
      if(btest(status,aoterr_Fatal).or.scale/=real(t-17,double_k)/8) error stop 'Computed real'
      call aot_table_open(L=state,thandle=table,key='mesh')
      if(table==0) error stop 'Nested table'
      if(aot_table_length(L=state,thandle=table)/=2) error stop 'Table length'
      call aot_get_val(L=state,thandle=table,key='nx',val=nx,ErrCode=status)
      if(btest(status,aoterr_Fatal).or.nx/=t+2) error stop 'nx'
      call aot_get_val(L=state,thandle=table,key='ny',val=ny,ErrCode=status)
      if(btest(status,aoterr_Fatal).or.ny/=3*t-4) error stop 'ny'
      call aot_table_close(L=state,thandle=table)
      call aot_get_val(L=state,key='absent',val=default_value,ErrCode=status,default=-t)
      if(btest(status,aoterr_Fatal).or..not.btest(status,aoterr_NonExistent)) error stop 'Default flags'
      if(default_value/=-t) error stop 'Default value'
      call close_config(L=state)
      open(newunit=unit,file='checked.lua',status='old')
      close(unit,status='delete')
   end subroutine
end program
