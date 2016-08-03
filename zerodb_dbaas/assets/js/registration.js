var submitting = false;
var appname = "zerodb.com";

$(document).ready(function() {
    $("form").submit(function() {
        var password = $("#inputPassword").val();
        var password2 = $("#inputPasswordConfirmation").val();

        if ((password2 != null) & (password != password2)) {
            $("#validation-error-message").html("ValidationError: passwords don't match");
            return false;
        }

        if (!submitting) {
            // Same algorithm as in zerodb.crypto.kdf
            // hash = sha256(scrypt(password, salt) + 'auth')

            var username = $("#inputEmail").val();
            var salt = username + "|" + appname + "|key";

            scrypt(password, salt, 14, 8, 32, 5000, function(out) {
                var hash = sjcl.bn.fromBits(
                    sjcl.codec.bytes.toBits(out));
                hash = sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(hash + 'auth'));
                $("#inputPassword").val(hash);
                if (password2 != null) {
                    $("#inputPasswordConfirmation").val(hash);
                }
                submitting = true;
                $("form").submit();
            });
            return false;
        } else {
            submitting = false;
            return true;
        }
    });
});
