! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   use iso_c_binding
   use lmdb
   implicit none
   type(c_ptr) :: env,txn
   type(mdb_val_type) :: key,value,found
   character(8),target :: key_text,value_text
   character(:),allocatable :: text
   integer :: db,i,unit,rc
   call check(mdb_env_create(env))
   call check(mdb_env_set_mapsize(env,1048576_c_size_t))
   call check(mdb_env_set_maxdbs(env,1))
   call check(mdb_env_open(env,'checked.mdb',MDB_NOSUBDIR,int(o'0600')))
   key%mv_size=8
   key%mv_data=c_loc(key_text)
   value%mv_size=8
   value%mv_data=c_loc(value_text)
   call check(mdb_txn_begin(env,c_null_ptr,0,txn))
   call check(mdb_dbi_open(txn,'numbers',MDB_CREATE,db))
   do i=1,64
      call select_key(i)
      write(value_text,'(i8.8)') i*i
      call check(mdb_put(txn,db,key,value,0))
   end do
   call check(mdb_txn_commit(txn))
   call verify(0)
   call check(mdb_txn_begin(env,c_null_ptr,0,txn))
   do i=1,64
      call select_key(i)
      value_text='99999999'
      call check(mdb_put(txn,db,key,value,0))
   end do
   call mdb_txn_abort(txn)
   call verify(0)
   call check(mdb_txn_begin(env,c_null_ptr,0,txn))
   do i=1,64
      call select_key(i)
      if(mod(i,3)==0) then
         call check(mdb_del(txn,db,key,c_null_ptr))
      else
         write(value_text,'(i8.8)') i*i+7
         call check(mdb_put(txn,db,key,value,0))
      end if
   end do
   call check(mdb_txn_commit(txn))
   call verify(1)
   call mdb_dbi_close(env,db)
   call mdb_env_close(env)
   open(newunit=unit,file='checked.mdb',status='old')
   close(unit,status='delete')
   open(newunit=unit,file='checked.mdb-lock',status='old')
   close(unit,status='delete')
   print '(a)', '192 key-state references: committed inserts, full rollback, updates and 21 deletions'
   print '(a)', 'PASS lmdb-rollback-reference'
contains
   subroutine select_key(n)
      integer,intent(in) :: n
      write(key_text,'(a,i6.6)') 'k-',n
   end subroutine
   subroutine check(code)
      integer,intent(in) :: code
      if(code/=MDB_SUCCESS) error stop 'LMDB API'
   end subroutine
   subroutine verify(phase)
      integer,intent(in) :: phase
      integer :: n,expected
      character(8) :: oracle
      call check(mdb_txn_begin(env,c_null_ptr,MDB_RDONLY,txn))
      do n=64,1,-1
         call select_key(n)
         rc=mdb_get(txn,db,key,found)
         if(phase==1.and.mod(n,3)==0) then
            if(rc/=MDB_NOTFOUND) error stop 'Deleted key found'
         else
            call check(rc)
            expected=n*n+7*phase
            write(oracle,'(i8.8)') expected
            call c_f_str_ptr(found%mv_data,text,found%mv_size)
            if(text/=oracle) error stop 'Committed value oracle'
         end if
      end do
      call mdb_txn_abort(txn)
   end subroutine
end program
