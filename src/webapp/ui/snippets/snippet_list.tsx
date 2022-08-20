import React from "react";
import {
  Box,
  Button,
  Icon,
  Stack,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { PartialSnippet } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppConfig, AppContext } from "../../config";

import { useAuth } from "../login/hooks";
import { Link, useNavigate, useParams } from "react-router-dom";
import { AddIcon, EditIcon } from "@chakra-ui/icons";
import { Result } from "neverthrow";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { SnippetBreadcrumb } from "../layout/breadcrumb";

type SnippetRowProps = {
  snippet: PartialSnippet;
};

type SnippetListTableProps = {
  config: AppConfig;
  token: string;
  snippetType: string;
};

export const SnippetRow: React.FunctionComponent<SnippetRowProps> = (
  props: SnippetRowProps
) => {
  const snippet = props.snippet;
  return (
    <Tr>
      <Td>{snippet.slug}</Td>
      <Td>{snippet.meta.type}</Td>
      <Td>
        <Link to={`/admin/snippets/edit/${snippet.meta.type}/${snippet.slug}`}>
          <Icon as={EditIcon} marginEnd={2} />
          Edit
        </Link>
      </Td>
    </Tr>
  );
};

export const SnippetListTable: React.FunctionComponent<
  SnippetListTableProps
> = (props: SnippetListTableProps) => {
  const { config, token, snippetType } = props;
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [snippets, setSnippets] = React.useState<PartialSnippet[]>([]);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadSubSites() {
      let snippets: Result<PartialSnippet[], ApiError>;
      snippets = await config.api.snippet.listSnippets(token, snippetType);
      snippets
        .map((snippets: PartialSnippet[]) => setSnippets(snippets))
        .mapErr((err: ApiError) => setError(err)); // FIXME
      setIsLoading(false);
    }
    loadSubSites();
    return function cleanup() {};
  }, []);

  if (isLoading) {
    return <Loader label="Loading snippet list" />;
  }
  if (error) {
    return <ApiErrorUI error={error} />;
  }
  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Slug</Th>
            <Th>Type</Th>
            <Th>Edit</Th>
          </Tr>
        </Thead>
        <Tbody>
          {snippets.map((snippet, i) => (
            <SnippetRow snippet={snippet} key={i} />
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

type SnippetListButtonsProps = {
  snippetType: string;
};
export const SnippetListButtons: React.FunctionComponent<
  SnippetListButtonsProps
> = (props: SnippetListButtonsProps) => {
  const snippetType = props.snippetType;
  let navigate = useNavigate();
  return (
    <Stack p={4} spacing={4} direction="row" align="right">
      <Button
        colorScheme="teal"
        onClick={() =>
          navigate(`/admin/snippets/new/${snippetType}`, { replace: true })
        }
      >
        <Icon as={AddIcon} marginEnd={2} />
        Add new snippet
      </Button>
    </Stack>
  );
};

export const SnippetList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const params = useParams();
  const snippetType = params.snippetType || "";

  return (
    <Box>
      <SnippetBreadcrumb snippetType={snippetType} />
      <SnippetListTable
        config={config}
        token={token}
        snippetType={snippetType}
      />
      <SnippetListButtons snippetType={snippetType} />
    </Box>
  );
};
