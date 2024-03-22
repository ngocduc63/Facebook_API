
def create_error_code(er_code, mess):
    return {
        'error_code': er_code,
        'mess': mess
    }


ERROR_DATA_NOT_MATCH = create_error_code(1, "data request not match")
ERROR_DB_NOT_FOUND = create_error_code(2, "data not found in DB")
ERROR_FORMAT_EMAIL = create_error_code(3, "email not format")
ERROR_FORMAT_PASSWORD = create_error_code(4, "password not format")
ERROR_FORMAT_DATE = create_error_code(5, "date not format(dd/mm/yyyy)")
ERROR_NOT_FOUND_EMAIL = create_error_code(6, " account not found in DB")
ERROR_PASSWORD_NOT_MATCH = create_error_code(7, "check password fail")
ERROR_USER_NOT_FOUND = create_error_code(8, "user not found in DB")
ERROR_ACCOUNT_EXIST = create_error_code(9, "account exist in DB")
ERROR_FILE_NULL = create_error_code(10, "file request null")
ERROR_UPLOAD_FILE = create_error_code(11, "error upload file in BE")
ERROR_CHECK_TOKEN = create_error_code(12, "check token fail")
ERROR_SAVE_DB = create_error_code(13, "can't save data in DB")
ERROR_POST_NOT_FOUND = create_error_code(14, "post not found in DB")
ERROR_LIKE_NOT_FOUND = create_error_code(15, "like not found in DB")
ERROR_COMMENT_NOT_FOUND = create_error_code(16, "comment not found in DB")
ERROR_LIKE_IN_POST_EXIST = create_error_code(17, "like in post exist")
ERROR_USER_HAVE_NOT_ROLE = create_error_code(18, "user haven't role admin")
ERROR_CAN_NOT_ADD_YOURSELF = create_error_code(19, "can't add yourself")
ERROR_CAN_NOT_ADD_FRIEND = create_error_code(20, "can't add because friend exist")
ERROR_FRIEND_NOT_FOUND = create_error_code(21, "friend not found in DB")
ERROR_CAN_NOT_CREATE_ROOM = create_error_code(22, "can't create room")
ERROR_PAGE_NUM_NULL = create_error_code(23, "page null")
