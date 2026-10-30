program command_line_namelist
   ! Adapted from urbanjost/M_CLI example/demo3.f90 (public domain).
   ! Edit the prototype below to experiment with command-line defaults.
   use M_CLI, only: commandline, check_commandline
   implicit none
   integer :: n, ios
   real :: scale, points(3)
   logical :: verbose
   character(len=32) :: title
   character(len=256) :: message
   character(len=:), allocatable :: text
   namelist /args/ n, scale, points, verbose, title

   text = commandline('-n 3 --scale 2.5 --points 1,2,3 --verbose T --title "demo"')
   read(text, nml=args, iostat=ios, iomsg=message)
   call check_commandline(ios, message)
   if (ios /= 0) error stop 'NAMELIST conversion failed'
   if (n /= 3 .or. abs(scale-2.5) > 1.e-6) error stop 'numeric options'
   if (any(abs(points-[1.,2.,3.]) > 1.e-6)) error stop 'array option'
   if (.not. verbose .or. title /= 'demo') error stop 'logical/string options'

   write(*, nml=args)
   print '(a,f8.3)', 'Scaled sum of points: ', scale*sum(points)
   print '(a)', 'PASS m_cli'
end program command_line_namelist
