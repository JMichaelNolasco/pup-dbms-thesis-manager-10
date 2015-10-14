$(function (){
var check = [];
var keywords = [];
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


function search (event)
    {   
        $('#searched').empty();
        var y = $("#searcher").val().toLowerCase();
        var searcher_api = '/api/search'
        $.post(searcher_api, JSON.stringify({ "y": y,}), function(response)
        {
            if (response.status == 'OK')
            {   
                if ($.isEmptyObject(response.searched))
                {
                    $('#searched').prepend("\"No match found.\"");
                }

                for(var index in response.searched) 
                {
                    if (response.searched[index]['thesis_title'])
                    {
                        var header = response.searched[index]['university'] + "<div style='float:right'>" +response.searched[index]['thesis_year'] + "</div><br>" + response.searched[index]['college'] + "<br>" + response.searched[index]['department'];
                        var title = response.searched[index]['thesis_title'];
                        $('#searched').prepend("<a class='mybtn' href='/thesis/edit/"+response.searched[index]['id']+"'><li>><div>"+header+"</div><div>"+title+"</div></li></a><hr>");
                    }
                    else
                    {
                        var name = response.searched[index]['student.stud_fname'] + " " + response.searched[index]['student.stud_mname'] + " " + response.searched[index]['student.stud_lname'];
                        $('#searched').prepend("<a class='mybtn' href='/student/page/"+response.searched[index]['id']+"'><li>" + name + "</li></a><hr>");
                    }

                }
                return false;
            }
            else alert('Error 192.168.1.11, Database error');
        })      
    }

var found = [];
$("select option").each(function() {
  if($.inArray(this.value, found) != -1) $(this).remove();
  found.push(this.value);
});

$(document).on('click', '.mybtn',function(){
        $(this).closest('li').remove();
    });
    //function for keywords checkboxes
    $('.keywords_cb').change(function() {
        s = $(this).attr('value');
        if ($(this).prop('checked')) 
        {
            keywords.push(s)
        }
        else {
            var index = keywords.indexOf(s);
            if (index >= 0) {
              keywords.splice( index, 1 );
            }
        }
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
