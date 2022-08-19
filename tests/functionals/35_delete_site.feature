Feature: As a user, I want to delete website

  Scenario: start an initialized session and wait
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    And a "/home/cat" page of type "blog:CategoryPage"
    And a "/home/dog" page of type "blog:CategoryPage"
    And a "cat.example.net" site with "/home/cat" root page
    And a "dog.example.net" site with "/home/dog" root page
    When I visit "/admin/sites/edit?hostname=cat.example.net"
    And I click on the "Delete this site" button
    And I click on the "Confirm Deletion" button
    Then I see the text "dog.example.net"
    And I don't see the text "cat.example.net"

