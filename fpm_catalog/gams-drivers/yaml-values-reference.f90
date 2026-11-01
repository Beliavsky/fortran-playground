! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use yafyaml
   implicit none
   integer :: trial
   do trial=1,32
      call fixture(trial)
   end do
   print '(a)', '32 fresh YAML files; 240 exact scalar/sequence references and absent keys'
   print '(a)', 'PASS yaml-values-reference'
contains
   subroutine fixture(t)
      integer,intent(in) :: t
      type(Parser) :: reader
      class(YAML_Node),allocatable :: document
      integer,allocatable :: samples(:)
      integer :: unit,n,j,rc,value
      logical :: enabled
      character(:),allocatable :: title
      character(20) :: expected
      write(expected,'(a,i0)') 'fixture-',t
      n=mod(t-1,8)+1
      open(newunit=unit,file='fixture.yaml',status='new',action='write')
      write(unit,'(a)') 'title: "'//trim(expected)//'"'
      write(unit,'(a,i0)') 'iterations: ',t-17
      if(mod(t,2)==0) then
         write(unit,'(a)') 'enabled: true'
      else
         write(unit,'(a)') 'enabled: false'
      end if
      write(unit,'(a)',advance='no') 'samples: ['
      do j=1,n
         if(j>1) write(unit,'(a)',advance='no') ', '
         write(unit,'(i0)',advance='no') 3*j-t
      end do
      write(unit,'(a)') ']'
      close(unit)
      reader=Parser('core')
      document=reader%load('fixture.yaml')
      call document%get(value,'iterations',rc=rc)
      if(rc/=YAFYAML_SUCCESS .or. value/=t-17) error stop 'YAML integer'
      call document%get(enabled,'enabled',rc=rc)
      if(rc/=YAFYAML_SUCCESS) error stop 'YAML logical type'
      if(enabled.neqv.(mod(t,2)==0)) error stop 'YAML logical value'
      call document%get(title,'title',rc=rc)
      if(rc/=YAFYAML_SUCCESS) error stop 'YAML text type'
      if(title/=trim(expected)) error stop 'YAML text value'
      call document%get(samples,'samples',rc=rc)
      if(rc/=YAFYAML_SUCCESS) error stop 'YAML sequence type'
      if(size(samples)/=n) error stop 'YAML sequence shape'
      if(any(samples/=[(3*j-t,j=1,n)])) error stop 'YAML sequence values'
      if(document%has('absent')) error stop 'YAML absent key'
      open(newunit=unit,file='fixture.yaml',status='old')
      close(unit,status='delete')
   end subroutine
end program
