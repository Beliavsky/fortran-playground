! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   use M_CLI, only: commandline,check_commandline
   implicit none
   integer :: trial,n,status
   real :: scale,points(3)
   logical :: verbose
   character(32) :: title,expected_title
   character(256) :: message
   character(512) :: prototype
   character(:),allocatable :: text
   namelist /args/ n,scale,points,verbose,title
   do trial=1,32
      write(expected_title,'(a,i0)') 'fixture ',trial
      write(prototype,'(a,i0,a,f8.3,a,3(f8.3,a),a,a)') '-n ',trial-17,' --scale ',real(trial-17)/8, &
         ' --points ',real(trial)/4,',',real(-trial)/8,',',real(trial+3)/2,' --verbose ', &
         merge('T','F',mod(trial,2)==0),' --title "'//trim(expected_title)//'"'
      text=commandline(trim(prototype))
      read(text,nml=args,iostat=status,iomsg=message)
      call check_commandline(status,message)
      if(status/=0) error stop 'NAMELIST conversion'
      if(n/=trial-17.or.scale/=real(trial-17)/8) error stop 'Scalar references'
      if(any(points/=[real(trial)/4,real(-trial)/8,real(trial+3)/2])) error stop 'Array references'
      if(verbose.neqv.(mod(trial,2)==0)) error stop 'Logical reference'
      if(title/=expected_title) error stop 'Quoted title reference'
   end do
   print '(a)', '32 NAMELIST prototypes; 224 exact integer/real/array/logical/quoted-string references'
   print '(a)', 'PASS cli-namelist-reference'
end program
