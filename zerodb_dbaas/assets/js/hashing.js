var appname = "zerodb.com";
var auth_const = [97, 117, 116, 104];  // [ord(c) for c in 'auth'];

function compute_hash(username, password, cb) {
    var salt = username + "|" + appname + "|key";
    scrypt(password, salt, 14, 8, 32, 5000, function(out) {
        var hash = sjcl.codec.bytes.toBits(out.concat(auth_const));
        hash = sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(hash));
        hash = 'hash::' + hash;
        cb(hash);
    });
}
