$(document).ready(function(){
  function getCookie(c_name) {
     if (document.cookie.length > 0) {
         c_start = document.cookie.indexOf(c_name + "=");
         if (c_start != -1) {
             c_start = c_start + c_name.length + 1;
             c_end = document.cookie.indexOf(";", c_start);
             if (c_end == -1) c_end = document.cookie.length;
             return unescape(document.cookie.substring(c_start, c_end));
         }
     }
     return "";
 }


 $('#disable_account').click(function(){

    if(confirm("Are you sure you want to disable this account")){
      $.ajax({
          headers:{
            'X-CSRFToken':getCookie('csrftoken'),
          },
          url:'/api/disable/'+$(".username").val().toLowerCase()+"/",
          method:'POST',
          data:{"password":window.prompt("Enter your password"),"username":$(".username").val().toLowerCase()},

          success: function(response,textStatus,xhr){
            // console.log(response);
            // console.log(textStatus);
            // console.log(xhr);
          
            if (response.status===200 && !response.disabled){
              var disabled_account =  "<h3><font color=green><div class=status_account>Your account Was Re-enabled</div></font></h3>";
              $('.content').append(disabled_account);
              $('.account_status').text('Disable Account')
              $('.status_account').fadeOut(2000) 

            }
            if(response.status===200 && response.disabled){
              var disabled_account =  "<h3><font color=red> <div class=status_account>Your account Was disabled</div></font></h3>";
              $('.content').append(disabled_account);
              $('.account_status').text('Re-enable Account')
              $('.status_account').fadeOut(2000)              
            }
            if(response.status===400){
              var invalid_password = "<h3><font color=red> <div class=wrong_password>You entered wrong password</div></font></h3>";
              $('.content').append(invalid_password);
              // $('#disable_account').prop('checked',false);
              if (response.disabled){
                console.log("I am disabled");
                $('#disable_account').prop('checked', true);
              }
              if (!response.disabled){
                $('#disable_account').prop('checked',false);
              }
              $('.status_account').fadeOut(2000)
              $('.wrong_password').fadeOut(2000)
            }
          },
          error:function(){
            console.log("Something wen wrong")
          }
        }).done(function(){
            console.log("Account was disabled");
        });
      }
   
   });

})
