import React from "react";
import { Box, Button, Heading, Icon, Stack, Table, TableContainer, Tbody, Td, Th, Thead, Tr } from "@chakra-ui/react";
import { PartialPage } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/components";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { AddIcon, ArrowRightIcon, EditIcon, ViewIcon } from "@chakra-ui/icons";
import { Result } from "neverthrow";


export const PageList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [pages, setPages] = React.useState<PartialPage[]>([]);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [params, setParams] = useSearchParams();
  const parentPath = params.get("parent");
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadPages() {
      let pages: Result<PartialPage[], ApiError>;
      console.log("loading pages")
      pages = await config.api.page.listPages(token, parentPath);
      console.log("pages loaded")
      pages.
        map((pages: PartialPage[]) => setPages(pages)).
        mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
      console.log("setIsLoading false done")
    }
    loadPages();
    return function cleanup() { };
  }, []);

  console.log(`Render page list ${isLoading}`)
  if (isLoading) {
    return <>list loading...</>
  }

  return (
    <Box>
      {
        !error &&
        <>
          <Heading>
            Pages
          </Heading>

          <Box paddingLeft={15}>
            <TableContainer>
              <Table variant='simple'>
                <Thead>
                  <Tr>
                    <Th>Page</Th>
                    <Th>Edit</Th>
                    <Th>View</Th>
                    <Th>Childs</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {
                    pages.map(
                      (page, i) =>
                        <Tr key={i}>
                          <Td>{page.title}</Td>
                          <Td>
                            <Link to={`/admin/page/edit${page.path}`}>
                              <Icon as={EditIcon} marginEnd={2} />
                              Edit
                            </Link>
                          </Td>
                          <Td>
                            <a href={`${page.path}`}>
                              <Icon as={ViewIcon} marginEnd={2} />
                              View
                            </a>
                          </Td>
                          <Td>
                            <a href={`/admin/pages/?parent=${page.path}`}>
                              <Icon as={ArrowRightIcon} marginEnd={2} />
                            </a>
                            <a href={`/admin/page/new/?parent=${page.path}&type=${page.type}`}>
                              <Icon as={AddIcon} marginEnd={2} />
                            </a>
                          </Td>
                        </Tr>
                    )}
                </Tbody>
              </Table>
            </TableContainer>
            <Stack spacing={4} direction='row' align='right'>
              <Button onClick={() => navigate("/admin/page/new", { "replace": true })}>
                <Icon as={AddIcon} marginEnd={2} />
                Add
              </Button>
            </Stack>
          </Box>
        </>
      }
      {/* TODO display error properly, just in cases */}
      {
        error &&
        <ul>
          {
            [...error.keys()].map((k) => <li> {error.get(k)} </li>)
          }
        </ul>
      }
    </Box>
  );
}
