from opensearchpy.exceptions import NotFoundError, AuthenticationException
from elastic_transport import ApiResponseMeta

# Test 404 - passing meta as second arg like the test does
meta = ApiResponseMeta(404, '1.1', {}, 0.01, None)
err = NotFoundError('repository_missing_exception', meta, '[repo_name] missing')
print("NotFoundError attributes (created like test):")
print(f'  hasattr meta: {hasattr(err, "meta")}')
if hasattr(err, 'meta'):
    print(f'  meta: {err.meta}')
    print(f'  meta.status: {err.meta.status}')
else:
    print(f'  NO meta attribute!')
print(f'  status_code: {getattr(err, "status_code", "N/A")}')
print(f'  info: {getattr(err, "info", "N/A")}')
print(f'  error: {getattr(err, "error", "N/A")}')
print(f'  args: {err.args}')
print()

# Try accessing the attributes directly 
try:
    print(f'Trying to access err.meta directly: {err.meta}')
    print(f'err.meta.status = {err.meta.status}')
except AttributeError as e:
    print(f'AttributeError when accessing err.meta: {e}')
