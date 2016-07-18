var curve = sjcl.ecc.curves['k256'];  // secp256k1
var submitting = false;
var realm = "ZERO";

$(document).ready(function() {
    $("form").submit(function() {
        var password = $("#inputPassword").val();
        var password2 = $("#inputPasswordConfirmation").val();

        if ((password2 != null) & (password != password2)) {
            $("#validation-error-message").html("ValidationError: passwords don't match");
            return false;
        }

        if (!submitting) {
            var username = $("#inputEmail").val();
            var salt = username + "|" + realm;

            scrypt(password, salt, 14, 8, 32, 5000, function(out) {
                var priv = sjcl.bn.fromBits(
                    sjcl.codec.bytes.toBits(out));
                var raw_pub = curve.G.mult(priv);
                var pub = new sjcl.ecc.ecdsa.publicKey(curve, raw_pub)
                    .serialize()
                    .point;
                $("#inputPassword").val(pub);
                if (password2 != null) {
                    $("#inputPasswordConfirmation").val(pub);
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
