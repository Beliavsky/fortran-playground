program main
   use aotus_module, only: flu_State, open_config_file, close_config, aot_get_val, &
      aoterr_Fatal, aoterr_NonExistent
   use aot_table_module, only: aot_table_open, aot_table_close, aot_table_length
   use flu_kinds_module, only: double_k
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(flu_State) :: config
   integer :: unit, status, steps, nx, ny, mesh, fallback
   real(double_k) :: scale

   open(newunit=unit, file='playground-config.lua', status='new', action='write', iostat=status)
   if (status /= 0) error stop 'cannot create configuration'
   write(unit,'(a)') 'steps = 3*4', 'scale = 1.5', 'mesh = {nx=4, ny=6}'
   close(unit)
   call open_config_file(L=config, filename='playground-config.lua', ErrCode=status)
   if (status /= 0) error stop 'configuration load failed'
   call aot_get_val(L=config, key='steps', val=steps, ErrCode=status)
   if (btest(status,aoterr_Fatal) .or. steps /= 12) error stop 'steps mismatch'
   call aot_get_val(L=config, key='scale', val=scale, ErrCode=status)
   if (btest(status,aoterr_Fatal)) error stop 'scale retrieval failed'
   if (.not. ieee_is_finite(scale)) error stop 'nonfinite scale'
   if (abs(scale-1.5_double_k) > 1e-12_double_k) error stop 'scale mismatch'
   call aot_table_open(L=config, thandle=mesh, key='mesh')
   if (mesh == 0) error stop 'mesh table missing'
   if (aot_table_length(L=config,thandle=mesh) /= 2) error stop 'mesh table length'
   call aot_get_val(L=config, thandle=mesh, key='nx', val=nx, ErrCode=status)
   if (btest(status,aoterr_Fatal) .or. nx /= 4) error stop 'nx mismatch'
   call aot_get_val(L=config, thandle=mesh, key='ny', val=ny, ErrCode=status)
   if (btest(status,aoterr_Fatal) .or. ny /= 6) error stop 'ny mismatch'
   call aot_table_close(L=config, thandle=mesh)
   call aot_get_val(L=config, key='missing', val=fallback, ErrCode=status, default=99)
   if (btest(status,aoterr_Fatal) .or. .not. btest(status,aoterr_NonExistent)) error stop 'default status'
   if (fallback /= 99) error stop 'default value mismatch'
   call close_config(L=config)
   print '(a,i0,a,f5.2)', 'Steps: ', steps, '  scale: ', scale
   print '(a,i0,a,i0)', 'Mesh: ', nx, ' by ', ny
   print '(a,i0)', 'Missing setting uses default: ', fallback
   open(newunit=unit, file='playground-config.lua', status='old', iostat=status)
   if (status /= 0) error stop 'cannot reopen configuration for cleanup'
   close(unit,status='delete')
   print *, 'PASS aotus'
end program
