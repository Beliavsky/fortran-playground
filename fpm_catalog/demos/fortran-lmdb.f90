! Transactions in a small sandbox-local LMDB database. Nothing is persisted.
program main
   use, intrinsic :: iso_c_binding
   use lmdb
   implicit none
   type(c_ptr) :: env, txn
   type(mdb_val_type) :: key, value, found
   character(5), target :: key_text = 'color'
   character(5), target :: first = 'green', second = 'amber'
   character(:), allocatable :: text
   integer :: db, rc, unit
   key%mv_size = len(key_text, kind=c_size_t)
   key%mv_data = c_loc(key_text)
   call check(mdb_env_create(env))
   call check(mdb_env_set_mapsize(env, 1048576_c_size_t))
   call check(mdb_env_set_maxdbs(env, 1))
   call check(mdb_env_open(env, 'playground.mdb', MDB_NOSUBDIR, int(o'0600')))
   call check(mdb_txn_begin(env, c_null_ptr, 0, txn))
   call check(mdb_dbi_open(txn, 'colors', MDB_CREATE, db))
   value%mv_size = len(first, kind=c_size_t)
   value%mv_data = c_loc(first)
   call check(mdb_put(txn, db, key, value, 0))
   call check(mdb_txn_commit(txn))
   call read_value('green')
   call check(mdb_txn_begin(env, c_null_ptr, 0, txn))
   value%mv_data = c_loc(second)
   call check(mdb_put(txn, db, key, value, 0))
   call check(mdb_txn_commit(txn))
   call read_value('amber')
   ! An aborted update must not replace the committed value.
   call check(mdb_txn_begin(env, c_null_ptr, 0, txn))
   value%mv_data = c_loc(first)
   call check(mdb_put(txn, db, key, value, 0))
   call mdb_txn_abort(txn)
   call read_value('amber')
   call check(mdb_txn_begin(env, c_null_ptr, 0, txn))
   call check(mdb_del(txn, db, key, c_null_ptr))
   call check(mdb_txn_commit(txn))
   call check(mdb_txn_begin(env, c_null_ptr, MDB_RDONLY, txn))
   rc = mdb_get(txn, db, key, found)
   if (rc /= MDB_NOTFOUND) error stop 'Deleted key still exists'
   call mdb_txn_abort(txn)
   call mdb_dbi_close(env, db)
   call mdb_env_close(env)
   open(newunit=unit, file='playground.mdb', status='old')
   close(unit, status='delete')
   open(newunit=unit, file='playground.mdb-lock', status='old')
   close(unit, status='delete')
   print '(a)', 'Delete and transaction rollback verified.'
   print '(a)', 'PASS fortran-lmdb'
contains
   subroutine check(status)
      integer, intent(in) :: status
      if (status == MDB_SUCCESS) return
      print '(a)', mdb_strerror(status)
      error stop 'LMDB operation failed'
   end subroutine check
   subroutine read_value(expected)
      character(*), intent(in) :: expected
      call check(mdb_txn_begin(env, c_null_ptr, MDB_RDONLY, txn))
      call check(mdb_get(txn, db, key, found))
      call c_f_str_ptr(found%mv_data, text, found%mv_size)
      if (text /= expected) error stop 'Incorrect database value'
      print '(a)', 'color = ' // text
      call mdb_txn_abort(txn)
   end subroutine read_value
end program main
