$(document).ready(function() {
    $("#new-instance-pwd").click(function() {
        var next_db_id = $("#next-db-id").val();
        var url = "/add_subdb";

        var password = $("#inputPassword").val();
        var password2 = $("#inputPasswordConfirmation").val();

        if ((password != password2) | (password2 == "") | (password == "")) {
            alert("Passwords don't match");  // XXX should be a proper message
            return false;
        }

        compute_hash(next_db_id, password, function(hash) {
            $.post(url, {'next_db_id': next_db_id, 'password': hash}, function(data) {
                if (data.ok == 1) {
                    $("#instanceModal").modal('hide');
                    $("#stripeModal").modal('show');
                }
            });
        });

        return false;
    });
});
