$(function (){
var check = [];
function onFormSubmit(event){
	

	var data= $(event.target).serializeArray();

	var thesis = {};
	for (var i=0; i<data.length; i++){
		thesis[data[i].name] = data[i].value 
	}

	//send data to server
	var thesis_create_api = '/api/thesis';
	


	$.post(thesis_create_api,thesis,function(response){	 //url,data,callback
		if (response.status = "ok"){

		}});

	var list_element=$('<li id="item"' +'class="' + thesis.year + thesis.title + '">');
	list_element.html(thesis.year + ' ' + thesis.title + ' '  + ' <input type=button class="buttn btn-danger  btn-xs" value="Delete"  > ');
	

	if  ($('ul.thesis-list li').hasClass(thesis.year + thesis.title))
	{
		alert('Duplicate entries found! .Try Again');
	}
	else
	{
		$(".thesis-list").prepend(list_element) ;
		check.push(thesis.year + ' ' + thesis.title);

	}
	

	 return false;

}



function loadAllthesis_list() {
    var thesis_list_api = '/api/thesis';

    $.get(thesis_list_api, {}, function(response){
    console.log('thesis list', response)
    response.data.forEach(function(thesis){
    
    $('.list-section tr:first').after('<tr></tr>');
    $('tr:eq(1)').append('<td>'+ thesis.university + '</td>');
    $('tr:eq(1)').append('<td>'+ thesis.college + '</td>') ;
    $('tr:eq(1)').append('<td>'+ thesis.department + '</td>');
    $('tr:eq(1)').append('<td>'+ thesis.year + '</td>');
    $('tr:eq(1)').append('<td>' + (' <a  href=\'/thesis/'+thesis.id+'\'>'+ thesis.title +'</a>')  + '</td>');
    $('tr:eq(1)').append('<td>'+ thesis.abstract + '</td>');
    $('tr:eq(1)').append('<td>'+ thesis.section + '</td>');
    $('tr:eq(1)').append('<td>'+ thesis.adviser + '</td>');

    $('tr:eq(1)' ).append('<td>'+ thesis.proponents + '</td>');
    $('tr:eq(1)').append('<td>'+ thesis.member_one + ' ' + thesis.member_two + ' ' + thesis.member_three + ' ' + 
                         thesis.member_four + ' ' + thesis.member_five + '</td>');

    $('tr:eq(1)').append('<td>'+  (' <a  href=\'/thesis/edit/'+thesis.id+'\'>Edit</a>')+ ' ' + ('<a href=\'/thesis/delete/'+thesis.id+'\'>Delete</a>')+ '</td>') ;
    
});
});
};


var found = [];
$("select option").each(function() {
  if($.inArray(this.value, found) != -1) $(this).remove();
  found.push(this.value);
});
       

//No Duplication of Dropdown Options
$(document).ready( function(){ 
        var a = new Array(); 
        $(".department").children("option").each(function(x){ 
                test = false; 
                b = a[x] = $(this).val(); 
                for (i=0;i<a.length-1;i++){ 
                        if (b ==a[i]) test =true; 
                } 
                if (test) $(this).remove(); 
        }) 
}); 
var warning = $(".message");


$(document).ready( function(){ 
        var a = new Array(); 
        $(".adviser").children("option").each(function(x){ 
                test = false; 
                b = a[x] = $(this).val(); 
                for (i=0;i<a.length-1;i++){ 
                        if (b ==a[i]) test =true; 
                } 
                if (test) $(this).remove(); 
        }) 
});




        
function DeleteEntry(event){
	$(this).parent().remove();
	$(this).closest('li').remove();
				
}

$(document).on('click',  '.buttn' , DeleteEntry)


$('.create-form').submit(onFormSubmit)
 // var selectedValues = $('#proponents').val();

// loadAllthesis_list()

$('.create-form').submit(function(onFormSubmit){ 
    this.reset();

$('input#contact').keyup(function(){
        if (
            ($(this).val().length > 0) && ($(this).val().substr(0,3) != '+63')
            || ($(this).val() == '')
            ){
            $(this).val('+63');    
        }
    });

function UserRegistration(event) {
        var data = $(event.target).serializeArray();

        var user = {};
        for (var i = 0; i < data.length; i++) {
            user[data[i].name] = data[i].value 
        }

        var users_create_api = '/api/user';
        $.post(users_create_api,user,function(response){	 //url,data,callback
		if (response.status = "ok"){
			alert("Succesful Registration")
			console.log("Users API Response Ok!");
			$(location).attr('href', '/home');
		}});

     
    }
   
$('.registration').submit(UserRegistration)





});

});
